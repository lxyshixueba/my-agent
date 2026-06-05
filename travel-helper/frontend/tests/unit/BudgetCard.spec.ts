/** BudgetCard 组件单元测试 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BudgetCard from '@/components/BudgetCard.vue'
import type { BudgetBreakdown } from '@/types/travelPlan'

/** 辅助函数：创建预算测试数据 */
function createBudget(overrides: Partial<BudgetBreakdown> = {}): BudgetBreakdown {
  return {
    attractionTickets: 500,
    hotelAccommodation: 2000,
    diningTransport: 300,
    diningFood: 800,
    total: 3600,
    ...overrides,
  }
}

describe('BudgetCard.vue', () => {
  it('正确渲染预算明细卡片', () => {
    const budget = createBudget()
    const wrapper = mount(BudgetCard, {
      props: { budget },
    })

    // 验证各分类金额
    expect(wrapper.text()).toContain('¥500.00')
    expect(wrapper.text()).toContain('¥2000.00')
    expect(wrapper.text()).toContain('¥300.00')
    expect(wrapper.text()).toContain('¥800.00')
  })

  it('正确渲染总费用', () => {
    const budget = createBudget({ total: 5280 })
    const wrapper = mount(BudgetCard, {
      props: { budget },
    })

    expect(wrapper.text()).toContain('预估总费用')
    expect(wrapper.text()).toContain('5280')
  })

  it('金额保留两位小数', () => {
    const budget = createBudget({
      attractionTickets: 100.5,
      hotelAccommodation: 2000,
      diningTransport: 300.333,
      diningFood: 800,
      total: 3200.833,
    })
    const wrapper = mount(BudgetCard, {
      props: { budget },
    })

    // el-statistic 的 precision 会控制小数位数
    expect(wrapper.text()).toContain('¥100.50')
    expect(wrapper.text()).toContain('¥2000.00')
  })

  it('显示预算明细标签文字', () => {
    const budget = createBudget()
    const wrapper = mount(BudgetCard, {
      props: { budget },
    })

    expect(wrapper.text()).toContain('景点门票')
    expect(wrapper.text()).toContain('酒店住宿')
    expect(wrapper.text()).toContain('餐饮交通')
    expect(wrapper.text()).toContain('餐饮食物')
  })
})
