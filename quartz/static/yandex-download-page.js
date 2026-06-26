const PUBLIC_KEY = "https://disk.yandex.ru/d/3yurdx5-APOkQQ"
const API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
const DOWNLOAD_RETRY_DELAY_MS = 2500
const DOWNLOAD_WINDOW_CLOSE_DELAY_MS = 12000

const statusEl = document.getElementById("status")
const pathEl = document.getElementById("file-path")
const retryEl = document.getElementById("retry")
const manualLinkEl = document.getElementById("manual-link")

const params = new URLSearchParams(window.location.search)
const sourcePath = params.get("p") || params.get("path") || ""
let directHref = ""
let directFilename = "download"

if (pathEl) {
  pathEl.textContent = sourcePath || "Путь к файлу не указан"
}

function setStatus(message, isError = false) {
  if (!statusEl) return
  statusEl.textContent = message
  statusEl.className = isError ? "error" : ""
}

function getFileName(path) {
  const rawName = path.split("/").filter(Boolean).pop()
  return rawName ? decodeURIComponent(rawName) : "download"
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (char) => {
    return (
      {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[char] || char
    )
  })
}

function openDownloadWindow(filename) {
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
      <p id="status">Запускаю скачивание...</p>
    </main>
  </body>
</html>`)
  downloadWindow.document.close()

  return downloadWindow
}

function setDownloadWindowStatus(downloadWindow, message) {
  try {
    const status = downloadWindow?.document.getElementById("status")
    if (status) status.textContent = message
  } catch {}
}

function closeDownloadWindowLater(downloadWindow) {
  if (!downloadWindow) return
  window.setTimeout(() => {
    try {
      if (!downloadWindow.closed) downloadWindow.close()
    } catch {}
  }, DOWNLOAD_WINDOW_CLOSE_DELAY_MS)
}

function startPopupDownload(href, filename) {
  const downloadWindow = openDownloadWindow(filename)
  if (!downloadWindow) {
    window.location.assign(href)
    return
  }

  setDownloadWindowStatus(
    downloadWindow,
    "Запускаю скачивание. Если первая попытка будет отклонена Яндексом, повторю автоматически...",
  )
  downloadWindow.location.href = href
  window.setTimeout(() => {
    try {
      if (!downloadWindow.closed) downloadWindow.location.href = href
    } catch {}
  }, DOWNLOAD_RETRY_DELAY_MS)
  closeDownloadWindowLater(downloadWindow)
}

function prepareManualDownload(href, filename) {
  if (manualLinkEl instanceof HTMLAnchorElement) {
    manualLinkEl.href = href
    manualLinkEl.download = filename
    manualLinkEl.hidden = false
  }
}

async function startDownload() {
  if (retryEl instanceof HTMLButtonElement) {
    retryEl.hidden = true
    retryEl.disabled = true
  }
  if (manualLinkEl instanceof HTMLAnchorElement) {
    manualLinkEl.hidden = true
    manualLinkEl.removeAttribute("href")
  }

  if (!sourcePath.startsWith("/")) {
    setStatus("Ошибка: ссылка не содержит корректный путь к файлу.", true)
    if (retryEl instanceof HTMLButtonElement) {
      retryEl.hidden = false
      retryEl.disabled = false
    }
    return
  }

  try {
    setStatus("Получаю актуальную ссылку Яндекс.Диска...")

    const url = new URL(API_URL)
    url.searchParams.set("public_key", PUBLIC_KEY)
    url.searchParams.set("path", sourcePath)

    const response = await fetch(url.toString(), { cache: "no-store" })
    if (!response.ok) {
      throw new Error(`Yandex Disk API returned ${response.status}`)
    }

    const data = await response.json()
    if (!data.href) {
      throw new Error("Yandex Disk API response does not contain href")
    }

    directHref = data.href
    directFilename = getFileName(sourcePath)
    prepareManualDownload(directHref, directFilename)
    setStatus("Ссылка готова. Нажми «Скачать файл вручную», чтобы запустить загрузку.")
  } catch (error) {
    console.error(error)
    setStatus(
      "Не удалось получить ссылку на скачивание. Проверь интернет или открой исходную папку Яндекс.Диска.",
      true,
    )
    if (retryEl instanceof HTMLButtonElement) {
      retryEl.hidden = false
      retryEl.disabled = false
    }
  }
}

manualLinkEl?.addEventListener("click", (event) => {
  if (!directHref || !(manualLinkEl instanceof HTMLAnchorElement)) return
  event.preventDefault()
  startPopupDownload(directHref, directFilename)
})

retryEl?.addEventListener("click", startDownload)
startDownload()
