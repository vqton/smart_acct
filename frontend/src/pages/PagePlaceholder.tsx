import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui'

export default function PagePlaceholder({ title = 'Trang đang phát triển' }: { title?: string }) {
  const navigate = useNavigate()
  return (
    <div className="flex flex-col items-center justify-center py-20 text-gray-400">
      <span className="text-6xl mb-4">🚧</span>
      <h2 className="text-xl font-semibold text-gray-600 mb-2">{title}</h2>
      <p className="text-sm mb-6">Chức năng này đang được xây dựng</p>
      <Button variant="secondary" onClick={() => navigate('/dashboard')}>Về trang chủ</Button>
    </div>
  )
}
