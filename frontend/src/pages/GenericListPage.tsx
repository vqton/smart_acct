import { PageHeader, DataTable } from '@/components/ui'

interface Props {
  title: string
  module: string
}

export default function GenericListPage({ title, module }: Props) {
  return (
    <div>
      <PageHeader
        title={title}
        subtitle={`Module: ${module}`}
        onAdd={{ label: 'Thêm mới', onClick: () => {} }}
      />
      <div className="mt-4">
        <DataTable
          columns={[
            { key: 'placeholder', label: 'Đang phát triển' },
          ]}
          data={[]}
          keyExtractor={() => '1'}
          emptyMessage={`Module ${module} đang được xây dựng. Vui lòng quay lại sau.`}
        />
      </div>
    </div>
  )
}
