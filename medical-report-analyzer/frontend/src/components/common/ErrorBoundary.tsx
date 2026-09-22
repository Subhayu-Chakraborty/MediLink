/**
 * components/common/ErrorBoundary.tsx
 * -------------------------------------
 * React class component error boundary — catches render errors in child tree.
 * // TODO: Implement in Phase 1
 */
import { Component, ErrorInfo, ReactNode } from 'react'

interface Props  { children: ReactNode; fallback?: ReactNode }
interface State  { hasError: boolean; error: Error | null }

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    // TODO: Implement in Phase 1
    return { hasError: true, error }
  }

  componentDidCatch(_error: Error, _info: ErrorInfo) {
    // TODO: Implement in Phase 1 — log to monitoring service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <div>Something went wrong.</div>
    }
    return this.props.children
  }
}

export default ErrorBoundary
