import useSWR from "swr"
import { DeleteDatasetApi, FetchDatasetApi, MaxKbDataset } from "../apis/files"
import { Link } from "react-router-dom"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const columns: ColumnDef<MaxKbDataset>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "name",
    header: "名称",
  },
  {
    accessorKey: "description",
    header: "描述",
  },
  {
    accessorKey: 'completed',
    header: '进度',
    cell: ({row}) => {
      return (
        <div>
          <span>{row.original.completed}</span>
          <span>/</span>
          <span>{row.original.total}</span>
        </div>
      )
    }
  },
  {
    accessorKey: "update_time",
    header: "更新时间",
  },
  {
    header: '管理文档',
    cell: ({row}) => {
      return (
        <Link to={`/library/detail/${row.id}/document/list`}>
          <Button variant="link">管理文档</Button>
        </Link>
      )
    }
  },
]

export const Libraries = () => {
  const { data, error, isLoading, mutate } = useSWR<MaxKbDataset[]>(FetchDatasetApi, () => fetch(FetchDatasetApi).then(r => r.json()))
  const table = useReactTable({
    data: data || [],
    columns,
    getRowId: row => `${row.id}`,
    getCoreRowModel: getCoreRowModel(),
  })
  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>

  const deleteButton = (
    <Button variant="destructive" onClick={async () => {
      const ids = table.getSelectedRowModel().rows.map(r => r.id)
      await fetch(DeleteDatasetApi, {
        method: "DELETE",
        body: JSON.stringify(ids),
        headers: {
          'Content-Type': 'application/json'
        }
      })
      mutate()
    }}>删除</Button>
  )

  return (
    <Card className="flex flex-col flex-1 m-2 ml-0 overflow-hidden">
      <CardHeader>
        <CardTitle>知识库管理</CardTitle>
        <CardDescription>您可以创建多个知识库，在与 AI 对话时，可以选择知识库上下文。</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col flex-1 gap-4">
        <div className="flex gap-2">
          <Link to="/library/create">
            <Button>创建知识库</Button>
          </Link>
          {deleteButton}
        </div>
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
