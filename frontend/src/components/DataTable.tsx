import type { ColumnDef } from "../types/index.js";

interface DataTableProps {
  columns: ColumnDef[];
  data: Record<string, unknown>[];
  loading: boolean;
  error: string | null;
  emptyMessage?: string;
}

export function DataTable({
  columns,
  data,
  loading,
  error,
  emptyMessage = "Không có dữ liệu",
}: DataTableProps) {
  if (loading) {
    return (
      <div className="table-status" role="status" aria-label="Đang tải">
        <div className="spinner" />
        <span>Đang tải...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="table-status table-status--error" role="alert">
        <span>Lỗi: {error}</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="table-status" role="status">
        <span>{emptyMessage}</span>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table className="data-table" role="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={col.width ? { width: col.width } : undefined}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={String(row.id ?? i)}>
              {columns.map((col) => (
                <td key={col.key}>
                  {col.render
                    ? col.render(row[col.key], row)
                    : String(row[col.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
