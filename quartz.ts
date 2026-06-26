import { loadQuartzConfig, loadQuartzLayout } from "./quartz/plugins/loader/config-loader"
import { Explorer, type ExplorerOptions } from "./.quartz/plugins"

type ExplorerNode = Parameters<NonNullable<ExplorerOptions["mapFn"]>>[0]

Explorer({
  order: ["filter", "sort", "map"],
  sortFn: (a: ExplorerNode, b: ExplorerNode) => {
    if ((!a.isFolder && !b.isFolder) || (a.isFolder && b.isFolder)) {
      const aName = a.isFolder
        ? (a.slugSegment ?? a.displayName ?? "")
        : (a.displayName ?? a.slugSegment ?? "")
      const bName = b.isFolder
        ? (b.slugSegment ?? b.displayName ?? "")
        : (b.displayName ?? b.slugSegment ?? "")

      return aName.localeCompare(bName, undefined, {
        numeric: true,
        sensitivity: "base",
      })
    }

    if (!a.isFolder && b.isFolder) {
      return 1
    }

    return -1
  },
  mapFn: (node: ExplorerNode) => {
    node.displayName = (node.displayName ?? node.slugSegment ?? "")
      .replace(/^\d{2}_/, "")
      .replace(/_/g, " ")
      .trim()
    return node
  },
})

const config = await loadQuartzConfig()
export default config
export const layout = await loadQuartzLayout()
