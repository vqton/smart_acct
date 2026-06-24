export interface AccountClass {
  id: string;
  code: string;
  name: string;
  classType: string;
  displayOrder: number;
  isActive: boolean;
}

export interface AccountType {
  id: string;
  code: string;
  name: string;
  classId: string;
  category: string;
  subType: string | null;
  isActive: boolean;
}

export interface BankGroup {
  id: string;
  code: string;
  name: string;
  groupType: string;
  isActive: boolean;
}

export interface TaxType {
  id: string;
  code: string;
  name: string;
  category: string;
  nature: string;
  calculationMethod: string;
  isActive: boolean;
}

export interface TaxCode {
  id: string;
  code: string;
  name: string;
  taxTypeId: string;
  taxRateType: string;
  application: string;
  isActive: boolean;
}

export interface GlAccount {
  id: string;
  code: string;
  name: string;
  category: string;
  nature: string;
  parentId: string | null;
  isActive: boolean;
  isPosting: boolean;
}

export interface StandardSection {
  key: string;
  label: string;
  endpoint: string;
  columns: ColumnDef[];
}

export interface ColumnDef {
  key: string;
  header: string;
  width?: string;
  render?: (value: unknown, row: Record<string, unknown>) => string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination?: { page: number; pageSize: number; totalItems: number; totalPages: number };
}
