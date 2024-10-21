import useSWR from "swr"
import SpinnerIcon from '@/assets/spinner.svg?react'
import { DeleteDocumentApi, FetchDocumentApi, MaxKbDocument } from "../apis/files"
import { Link, useParams } from "react-router-dom"
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
import { Label } from "@/components/ui/label"

const columns: ColumnDef<MaxKbDocument>[] = [
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
    header: "文件名",
  },
  {
    accessorKey: "status",
    header: "状态",
  },
  {
    accessorKey: "create_time",
    header: "创建时间",
  },
  {
    accessorKey: "update_time",
    header: "更新时间",
  },
]

export const Documents = () => {
  const {id} = useParams<{id: string}>()
  const { data, error, isLoading, mutate } = useSWR<MaxKbDocument[]>(FetchDocumentApi({dataset_id: id}), () => fetch(FetchDocumentApi({dataset_id: id})).then(r => r.json()))
  const table = useReactTable({
    data: data || [],
    columns,
    getRowId: row => `${row.id}`,
    getCoreRowModel: getCoreRowModel(),
  })

  const tableElement = (
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
  )

  return (
    <Card className="flex flex-col flex-1 m-2 ml-0 overflow-hidden">
      <CardHeader>
        <CardTitle>文档管理</CardTitle>
        <CardDescription>上传文档，并将文档向量化。</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col flex-1 gap-4">
        <div className="flex gap-2">
          <Link to={`/library/detail/${id}/document/create`}>
            <Button>上传文档</Button>
          </Link>
          <Button variant="destructive" onClick={async () => {
            const ids = table.getSelectedRowModel().rows.map(r => r.id)
            await fetch(DeleteDocumentApi({dataset_id: id}), {
              method: "DELETE",
              body: JSON.stringify(ids),
              headers: {
                'Content-Type': 'application/json'
              }
            })
            mutate()
          }}>删除文档</Button>
        </div>
        {isLoading && <SpinnerIcon/>}
        {error && <Label>出错啦</Label>}
        {!isLoading && !error && tableElement}
      </CardContent>
    </Card>
  )
}
