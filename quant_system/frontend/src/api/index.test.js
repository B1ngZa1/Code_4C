import { describe, expect, it, beforeEach } from 'vitest'

import api from './index'

describe('api', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('adds Authorization header from localStorage token', () => {
    localStorage.setItem('token', 't1')
    const handler = api.interceptors.request.handlers[0].fulfilled
    const cfg = handler({ headers: {} })
    expect(cfg.headers.Authorization).toBe('Bearer t1')
  })
})

