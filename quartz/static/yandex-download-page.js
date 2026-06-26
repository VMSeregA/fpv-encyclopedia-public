const PUBLIC_KEY = "https://disk.yandex.ru/d/3yurdx5-APOkQQ"
const API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

const statusEl = document.getElementById("status")
const pathEl = document.getElementById("file-path")
const retryEl = document.getElementById("retry")
const manualLinkEl = document.getElementById("manual-link")

const params = new URLSearchParams(window.location.search)
const sourcePath = params.get("p") || params.get("path") || ""

if (pathEl) {
  pathEl.textContent = sourcePath || "Путь к файлу не указан"
}

function setStatus(message, isError = false) {
  if (!statusEl) return
  statusEl.textContent = message
  statusEl.className = isError ? "error" : ""
}

function startBrowserDownload(href) {
  if (manualLinkEl instanceof HTMLAnchorElement) {
    manualLinkEl.href = href
    manualLinkEl.download = ""
    manualLinkEl.hidden = false
  }

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

    setStatus("Ссылка готова. Скачивание должно начаться автоматически.")
    startBrowserDownload(data.href)
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

retryEl?.addEventListener("click", startDownload)
startDownload()
