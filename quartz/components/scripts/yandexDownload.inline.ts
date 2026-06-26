const YANDEX_DOWNLOAD_HELPER_PATH = "/static/yandex-download.html"
const YANDEX_PUBLIC_KEY = "https://disk.yandex.ru/d/3yurdx5-APOkQQ"
const YANDEX_DOWNLOAD_API = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

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

function startBrowserDownload(href: string): void {
  const link = document.createElement("a")
  link.href = href
  link.download = ""
  link.rel = "noopener"
  link.dataset.routerIgnore = ""
  link.style.display = "none"
  document.body.appendChild(link)
  link.click()
  link.remove()
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

    const previousTitle = anchor.title
    anchor.dataset.downloadState = "loading"
    anchor.title = "Получаю ссылку на скачивание..."

    try {
      const href = await resolveYandexDownloadHref(sourcePath)
      startBrowserDownload(href)
      anchor.title = "Скачивание запущено"
    } catch (error) {
      console.error(error)
      anchor.title = previousTitle
      window.location.assign(anchor.href)
    } finally {
      delete anchor.dataset.downloadState
    }
  },
  { capture: true },
)
