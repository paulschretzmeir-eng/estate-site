// Simple mock auth util
export function login(user) {
  localStorage.setItem('re_user', JSON.stringify(user))
}
export function logout() {
  localStorage.removeItem('re_user')
}
export function isAuthenticated() {
  return !!localStorage.getItem('re_user')
}
export function currentUser() {
  const raw = localStorage.getItem('re_user')
  return raw ? JSON.parse(raw) : null
}
