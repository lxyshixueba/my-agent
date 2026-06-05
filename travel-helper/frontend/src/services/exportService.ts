/** 导出服务 — 封装 html2canvas + jsPDF 导出逻辑 */

import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'

/** A4 纸张尺寸（单位 mm） */
const A4_WIDTH_MM = 210
const A4_HEIGHT_MM = 297
const A4_WIDTH_PX = 794
/** 页面边距（mm） */
const MARGIN_MM = 10

/**
 * 将 DOM 元素导出为图片并触发下载
 * @param element 要导出的 DOM 元素
 * @param filename 文件名（不含扩展名），默认 'travel-plan'
 */
export async function exportAsImage(
  element: HTMLElement,
  filename: string = 'travel-plan',
  onProgress?: (percent: number) => void,
): Promise<void> {
  onProgress?.(10)

  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
  })

  onProgress?.(80)

  // 将 canvas 转换为图片数据
  const dataUrl = canvas.toDataURL('image/png', 1.0)

  // 触发下载
  triggerDownload(dataUrl, `${filename}.png`)

  onProgress?.(100)
}

/**
 * 将 DOM 元素导出为 PDF 并触发下载
 * 自动分页处理：捕获多个 section，逐页添加到 PDF
 * @param sections 要导出的 DOM 元素数组（每个 section 作为一页或跨页内容）
 * @param filename 文件名（不含扩展名），默认 'travel-plan'
 */
export async function exportAsPdf(
  sections: HTMLElement[],
  filename: string = 'travel-plan',
  onProgress?: (percent: number) => void,
): Promise<void> {
  onProgress?.(10)

  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  })

  const contentWidthMm = A4_WIDTH_MM - MARGIN_MM * 2 // 扣除左右边距

  for (let i = 0; i < sections.length; i++) {
    const section = sections[i]

    // 捕获当前 section
    const canvas = await html2canvas(section, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
    })

    // 如果不是第一个 section，添加新页
    if (i > 0) {
      pdf.addPage()
    }

    // 计算图片在 PDF 中的尺寸
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height
    const imgRatio = canvasHeight / canvasWidth
    const imgWidthMm = contentWidthMm
    const imgHeightMm = imgWidthMm * imgRatio

    // 将 canvas 转换为图片数据
    const imgData = canvas.toDataURL('image/jpeg', 0.92)

    // 如果图片高度超过一页，需要分割
    const pageHeightMm = A4_HEIGHT_MM - MARGIN_MM * 2
    if (imgHeightMm > pageHeightMm) {
      // 计算需要多少页
      const totalPages = Math.ceil(imgHeightMm / pageHeightMm)
      let remainingHeight = imgHeightMm
      let yOffset = 0

      for (let page = 0; page < totalPages; page++) {
        if (page > 0) {
          pdf.addPage()
        }

        // 计算当前页要显示的部分
        const sliceHeight = Math.min(remainingHeight, pageHeightMm)

        // 创建一个临时 canvas 来截取当前页的部分
        const sliceCanvas = document.createElement('canvas')
        const sliceCtx = sliceCanvas.getContext('2d')
        if (sliceCtx) {
          // 计算源图像的像素对应关系
          const pxPerMm = canvasWidth / imgWidthMm
          const srcY = Math.floor(yOffset * pxPerMm)
          const srcH = Math.floor(sliceHeight * pxPerMm)

          sliceCanvas.width = canvasWidth
          sliceCanvas.height = Math.min(srcH, canvasHeight - srcY)

          sliceCtx.drawImage(canvas, 0, srcY, canvasWidth, sliceCanvas.height, 0, 0, canvasWidth, sliceCanvas.height)

          const sliceImgData = sliceCanvas.toDataURL('image/jpeg', 0.92)
          pdf.addImage(sliceImgData, 'JPEG', MARGIN_MM, MARGIN_MM, imgWidthMm, sliceHeight)
        }

        yOffset += pageHeightMm
        remainingHeight -= pageHeightMm
      }
    } else {
      // 一页可以容纳，直接添加
      pdf.addImage(imgData, 'JPEG', MARGIN_MM, MARGIN_MM, imgWidthMm, imgHeightMm)
    }

    onProgress?.(10 + ((i + 1) / sections.length) * 80)
  }

  pdf.save(`${filename}.pdf`)
  onProgress?.(100)
}

/**
 * 触发浏览器下载
 * @param dataUrl 图片数据 URL
 * @param filename 文件名
 */
function triggerDownload(dataUrl: string, filename: string): void {
  const link = document.createElement('a')
  link.href = dataUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 获取导出内容中需要捕获的 DOM 元素
 * 跳过地图等复杂 DOM 组件
 * @param containerId 容器元素 ID
 * @returns 需要导出的 DOM 元素数组
 */
export function getExportSections(containerId: string): HTMLElement[] {
  const container = document.getElementById(containerId)
  if (!container) {
    console.warn(`未找到容器元素: ${containerId}`)
    return []
  }

  const sections: HTMLElement[] = []

  // 获取容器直接子元素中需要导出的部分
  // 排除地图组件（data-skip-export 标记的元素）
  const children = container.children
  for (let i = 0; i < children.length; i++) {
    const child = children[i] as HTMLElement

    // 跳过标记为跳过导出的元素（如地图）
    if (child.dataset.skipExport === 'true') {
      continue
    }

    // 跳过隐藏元素
    if (child.offsetParent === null && child.tagName !== 'TEMPLATE') {
      continue
    }

    sections.push(child)
  }

  return sections
}
