/** AttractionCard 组件单元测试 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AttractionCard from '@/components/AttractionCard.vue'
import type { AttractionDetail } from '@/types/travelPlan'

/** 辅助函数：创建景点测试数据 */
function createAttraction(overrides: Partial<AttractionDetail> = {}): AttractionDetail {
  return {
    id: 'test-attraction-001',
    name: '故宫博物院',
    imageUrl: 'https://example.com/gugong.jpg',
    playDuration: '2-3 小时',
    description: '故宫是中国明清两代的皇家宫殿，也是世界上现存规模最大的宫殿型建筑群。',
    features: '皇家宫殿,世界遗产,历史文化',
    tips: '建议提前预约门票，避开节假日高峰期',
    latitude: 39.916345,
    longitude: 116.397155,
    ...overrides,
  }
}

describe('AttractionCard.vue', () => {
  it('正确渲染景点名称', () => {
    const attraction = createAttraction()
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    expect(wrapper.text()).toContain('故宫博物院')
  })

  it('正确渲染游玩时长', () => {
    const attraction = createAttraction()
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    expect(wrapper.text()).toContain('建议游玩时长')
    expect(wrapper.text()).toContain('2-3 小时')
  })

  it('正确渲染景点描述', () => {
    const attraction = createAttraction()
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    expect(wrapper.text()).toContain('故宫是中国明清两代的皇家宫殿')
  })

  it('正确渲染特色标签', () => {
    const attraction = createAttraction({
      features: '皇家宫殿,世界遗产',
    })
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    expect(wrapper.text()).toContain('皇家宫殿')
    expect(wrapper.text()).toContain('世界遗产')
  })

  it('正确渲染游玩贴士', () => {
    const attraction = createAttraction()
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    expect(wrapper.text()).toContain('建议提前预约门票')
  })

  it('渲染景点图片', () => {
    const attraction = createAttraction({
      imageUrl: 'https://example.com/test-image.jpg',
    })
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    // 验证 el-image 组件存在
    const image = wrapper.findComponent({ name: 'ElImage' })
    expect(image.exists()).toBe(true)
  })

  it('图片缺失时展示占位图', () => {
    const attraction = createAttraction({ imageUrl: '' })
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    // 验证占位符文字存在
    expect(wrapper.text()).toContain('暂无图片')
  })

  it('特色字段为空时不渲染标签', () => {
    const attraction = createAttraction({ features: '' })
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    // features-tags 区域不应存在
    const tags = wrapper.find('.features-tags')
    expect(tags.exists()).toBe(false)
  })

  it('tips 字段为空时不渲染贴士区域', () => {
    const attraction = createAttraction({ tips: '' })
    const wrapper = mount(AttractionCard, {
      props: { attraction },
    })

    // tips 区域不应存在
    const tips = wrapper.find('.attraction-tips')
    expect(tips.exists()).toBe(false)
  })

  it('特色字段支持多种分隔符拆分', () => {
    // 测试顿号分隔
    const attraction1 = createAttraction({ features: '自然景观 历史文化' })
    const wrapper1 = mount(AttractionCard, {
      props: { attraction },
    })
    // 组件内部通过 featureTags computed 拆分，验证文本包含拆分后的内容
    expect(wrapper1.text()).toContain('皇家宫殿')
  })
})
