/**
 * pages/NotFoundPage.tsx
 * -----------------------
 * 404 page shown when no route matches.
 * // TODO: Implement in Phase 1
 */
import type { FC } from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage: FC = () => (
  <main style={{ textAlign: 'center', padding: '4rem' }}>
    <h1>404 — Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <Link to="/login">Return to Login</Link>
  </main>
)

export default NotFoundPage
