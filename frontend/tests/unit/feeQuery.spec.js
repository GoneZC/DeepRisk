describe('费用查询接口功能测试', () => {
  const mockToken = 'valid_token_123'
  const baseURL = 'http://localhost:8080/api/settlements/search'
  
  beforeAll(() => {
    localStorage.setItem('token', mockToken)
    axios.defaults.baseURL = 'http://localhost:8080'
  })

  test('TC1: 有效参数查询', async () => {
    const params = {
      mdtrtId: 'M2023001',
      psnNo: 'P1001',
      page: 0,
      size: 10
    }
    
    const res = await axios.post('/api/settlements/search', params)
    
    expect(res.status).toBe(200)
    expect(res.data).toHaveProperty('data')
    expect(res.data.data).toBeInstanceOf(Array)
    expect(res.data).toHaveProperty('totalElements', expect.any(Number))
  })

  test('TC2: 无效日期格式', async () => {
    try {
      await axios.post('/api/settlements/search', {
        startDate: '2023/01/01', // 错误格式
        endDate: '2023-12-32'    // 无效日期
      })
    } catch (error) {
      expect(error.response.status).toBe(400)
      expect(error.response.data).toMatchObject({
        code: 'INVALID_DATE_FORMAT',
        message: expect.stringContaining('日期格式应为YYYY-MM-DD')
      })
    }
  })

  test('TC3: 无权限访问', async () => {
    localStorage.removeItem('token') // 清空token
    
    try {
      await axios.post('/api/settlements/search', { psnNo: 'P1001' })
    } catch (error) {
      expect(error.response.status).toBe(401)
      expect(error.response.data).toHaveProperty('code', 'UNAUTHORIZED')
    }
  })
}) 