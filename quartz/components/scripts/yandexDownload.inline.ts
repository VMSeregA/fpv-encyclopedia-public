const YANDEX_DOWNLOAD_HELPER_PATH = "/static/yandex-download.html"
const YANDEX_PUBLIC_KEY = "https://disk.yandex.ru/d/3yurdx5-APOkQQ"
const YANDEX_DOWNLOAD_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
const YANDEX_DOWNLOAD_RETRY_DELAY_MS = 2500
const YANDEX_DOWNLOAD_WINDOW_CLOSE_DELAY_MS = 12000

function isNormalDownloadClick(event: MouseEvent): boolean {
  return event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey
}

function getYandexDownloadPath(anchor: HTMLAnchorElement): string | null {
  try {
    const url = new URL(anchor.href)
    if (!url.pathname.endsWith(YANDEX_DOWNLOAD_HELPER_PATH)) return null
    const sourcePath = url.searchParams.get("p") || url.searchParams.get("path")
    return sourcePath?.startsWith("/") ? sourcePath : null
  } catch {
    return null
  }
}

function getFileName(sourcePath: string): string {
  const fallbackName = "download"
  const rawName = sourcePath.split("/").filter(Boolean).pop()
  return rawName ? decodeURIComponent(rawName) : fallbackName
}

function escapeHtml(text: string): string {
  return text.replace(
    /[&<>"']/g,
    (char) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      })[char] ?? char,
  )
}

async function resolveYandexDownloadHref(sourcePath: string): Promise<string> {
  const url = new URL(YANDEX_DOWNLOAD_API)
  url.searchParams.set("public_key", YANDEX_PUBLIC_KEY)
  url.searchParams.set("path", sourcePath)

  const response = await fetch(url.toString(), { cache: "no-store" })
  if (!response.ok) {
    throw new Error(`Yandex Disk API returned ${response.status}`)
  }

  const payload = await response.json()
  if (typeof payload.href !== "string" || payload.href.length === 0) {
    throw new Error("Yandex Disk API response does not contain href")
  }

  return payload.href
}

function openDownloadWindow(filename: string): Window | null {
  const downloadWindow = window.open("", "_blank")
  if (!downloadWindow) return null

  const safeFilename = escapeHtml(filename)
  downloadWindow.document.open()
  downloadWindow.document.write(`<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <title>Скачивание файла</title>
    <style>
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #101312;
        color: #edf7f4;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      main {
        max-width: 560px;
        padding: 28px;
        line-height: 1.5;
      }
      h1 {
        margin: 0 0 12px;
        font-size: 26px;
      }
      p {
        margin: 8px 0 0;
        color: #a7b9b3;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>Подготавливаю скачивание</h1>
      <p>Файл: ${safeFilename}</p>
      <p id="status">Получаю свежую ссылку Яндекс.Диска...</p>
    </main>
  </body>
</html>`)
  downloadWindow.document.close()

  return downloadWindow
}

function setDownloadWindowStatus(downloadWindow: Window | null, message: string): void {
  try {
    const status = downloadWindow?.document.getElementById("status")
    if (status) status.textContent = message
  } catch {}
}

function closeDownloadWindowLater(downloadWindow: Window | null): void {
  if (!downloadWindow) return
  window.setTimeout(() => {
    try {
      if (!downloadWindow.closed) downloadWindow.close()
    } catch {}
  }, YANDEX_DOWNLOAD_WINDOW_CLOSE_DELAY_MS)
}

function startPopupDownload(downloadWindow: Window | null, href: string): boolean {
  if (!downloadWindow || downloadWindow.closed) return false

  setDownloadWindowStatus(
    downloadWindow,
    "Запускаю скачивание. Если первая попытка будет отклонена Яндексом, повторю автоматически...",
  )

  downloadWindow.location.href = href
  window.setTimeout(() => {
    try {
      if (!downloadWindow.closed) downloadWindow.location.href = href
    } catch {}
  }, YANDEX_DOWNLOAD_RETRY_DELAY_MS)
  closeDownloadWindowLater(downloadWindow)

  return true
}

function closeDownloadWindow(downloadWindow: Window | null): void {
  try {
    if (downloadWindow && !downloadWindow.closed) downloadWindow.close()
  } catch {}
}

function fallbackToHelper(anchor: HTMLAnchorElement): void {
  window.location.assign(anchor.href)
}

document.addEventListener(
  "click",
  async (event) => {
    if (!(event instanceof MouseEvent) || !isNormalDownloadClick(event)) return
    const target = event.target instanceof Element ? event.target : null
    const anchor = target?.closest("a")
    if (!(anchor instanceof HTMLAnchorElement)) return

    const sourcePath = getYandexDownloadPath(anchor)
    if (!sourcePath) return

    event.preventDefault()
    event.stopPropagation()

    const filename = getFileName(sourcePath)
    const downloadWindow = openDownloadWindow(filename)
    const previousTitle = anchor.title
    anchor.dataset.downloadState = "loading"
    anchor.title = "Получаю ссылку на скачивание..."

    try {
      const href = await resolveYandexDownloadHref(sourcePath)
      if (!startPopupDownload(downloadWindow, href)) {
        fallbackToHelper(anchor)
      }
      anchor.title = "Скачивание запущено"
    } catch (error) {
      console.error(error)
      closeDownloadWindow(downloadWindow)
      anchor.title = previousTitle
      fallbackToHelper(anchor)
    } finally {
      delete anchor.dataset.downloadState
    }
  },
  { capture: true },
)
