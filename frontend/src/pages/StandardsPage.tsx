import { useState, useEffect, useCallback } from "react";
import { DataTable } from "../components/DataTable.js";
import { getAccountClasses, getAccountTypes, getBankGroups, getTaxTypes, getTaxCodes, getGlAccounts } from "../api/client.js";
import type { ColumnDef } from "../types/index.js";

interface TabDef {
  key: string;
  label: string;
  columns: ColumnDef[];
  fetcher: () => Promise<unknown[]>;
}

const booleanRender = (v: unknown) => (v ? "Có" : "Không");

const tabs: TabDef[] = [
  {
    key: "account-classes",
    label: "Loại TK kế toán",
    columns: [
      { key: "code", header: "Mã", width: "80px" },
      { key: "name", header: "Tên loại" },
      { key: "classType", header: "Phân loại", width: "120px" },
      { key: "displayOrder", header: "STT", width: "60px" },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getAccountClasses as () => Promise<unknown[]>,
  },
  {
    key: "account-types",
    label: "Loại tài khoản",
    columns: [
      { key: "code", header: "Mã", width: "80px" },
      { key: "name", header: "Tên loại" },
      { key: "category", header: "Nhóm", width: "150px" },
      { key: "subType", header: "Loại phụ", width: "120px" },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getAccountTypes as () => Promise<unknown[]>,
  },
  {
    key: "bank-groups",
    label: "Nhóm ngân hàng",
    columns: [
      { key: "code", header: "Mã", width: "80px" },
      { key: "name", header: "Tên nhóm" },
      { key: "groupType", header: "Loại", width: "130px" },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getBankGroups as () => Promise<unknown[]>,
  },
  {
    key: "tax-types",
    label: "Loại thuế",
    columns: [
      { key: "code", header: "Mã", width: "80px" },
      { key: "name", header: "Tên loại thuế" },
      { key: "category", header: "Nhóm", width: "150px" },
      { key: "calculationMethod", header: "Phương pháp", width: "130px" },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getTaxTypes as () => Promise<unknown[]>,
  },
  {
    key: "tax-codes",
    label: "Mã thuế",
    columns: [
      { key: "code", header: "Mã", width: "80px" },
      { key: "name", header: "Tên mã thuế" },
      { key: "taxRateType", header: "Loại thuế suất", width: "120px" },
      { key: "application", header: "Áp dụng", width: "100px" },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getTaxCodes as () => Promise<unknown[]>,
  },
  {
    key: "gl-accounts",
    label: "Tài khoản kế toán",
    columns: [
      { key: "code", header: "Số TK", width: "80px" },
      { key: "name", header: "Tên tài khoản" },
      { key: "category", header: "Phân loại", width: "140px" },
      { key: "nature", header: "Bản chất", width: "80px" },
      { key: "isPosting", header: "Hạch toán", width: "90px", render: booleanRender },
      { key: "isActive", header: "Kích hoạt", width: "90px", render: booleanRender },
    ],
    fetcher: getGlAccounts as () => Promise<unknown[]>,
  },
];

export function StandardsPage() {
  const [activeTab, setActiveTab] = useState(tabs[0]?.key ?? "");
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentTab = tabs.find((t) => t.key === activeTab) ?? tabs[0]!;

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await currentTab.fetcher();
      setData(result as Record<string, unknown>[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lỗi không xác định");
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [currentTab]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="page">
      <h1 className="page-title">Danh mục hệ thống</h1>
      <div className="tabs" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            aria-selected={tab.key === activeTab}
            className={`tab${tab.key === activeTab ? " tab--active" : ""}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="tab-content" role="tabpanel">
        <DataTable
          columns={currentTab.columns}
          data={data}
          loading={loading}
          error={error}
          emptyMessage={`Không có ${currentTab.label.toLowerCase()}`}
        />
      </div>
    </div>
  );
}
