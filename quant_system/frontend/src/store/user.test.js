import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../api', () => {
  return {
    default: {
      post: vi.fn(),
      get: vi.fn(),
    },
  }
})

import api from '../api'
import { useUserStore } from './user'

describe('user store', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    api.post.mockReset()
    api.get.mockReset()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('login success sets token and isLoggedIn', async () => {
    api.post.mockResolvedValueOnce({ data: { access_token: 'tok' } })
    api.get.mockResolvedValueOnce({ data: { id: 1, username: 'admin' } })

    const s = useUserStore()
    const ok = await s.login('admin', '123456')
    expect(ok).toBe(true)
    expect(s.token).toBe('tok')
    expect(localStorage.getItem('token')).toBe('tok')
    expect(s.isLoggedIn).toBe(true)
    expect(s.user).toEqual({ id: 1, username: 'admin' })
  })

  it('login failure returns false and keeps logged out', async () => {
    api.post.mockRejectedValueOnce(new Error('bad'))

    const s = useUserStore()
    const ok = await s.login('admin', 'bad')
    expect(ok).toBe(false)
    expect(s.isLoggedIn).toBe(false)
  })

  it('logout clears token and user', () => {
    localStorage.setItem('token', 'tok')
    const s = useUserStore()
    s.token = 'tok'
    s.user = { id: 1 }
    s.isLoggedIn = true

    s.logout()
    expect(s.token).toBe('')
    expect(s.user).toBe(null)
    expect(s.isLoggedIn).toBe(false)
    expect(localStorage.getItem('token')).toBe(null)
  })
})
