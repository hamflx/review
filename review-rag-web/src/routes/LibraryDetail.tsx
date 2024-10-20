import useSWR from "swr"
import { DeleteDocumentApi, FetchDocumentApi, MaxKbDocument } from "../apis/files"
import { Link, useParams } from "react-router-dom"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { ColumnDef, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table"
import { Checkbox } from "@/components/ui/checkbox"

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
    accessorKey: "filename",
    header: "文件名",
  },
  {
    accessorKey: "create_time",
    header: "创建时间",
  },
  {
    accessorKey: "creator",
    header: "创建人",
  },
  {
    accessorKey: "update_time",
    header: "更新时间",
  },
  {
    accessorKey: "updater",
    header: "更新人",
  },
  {
    accessorKey: "md5",
    header: "MD5",
  },
  {
    accessorKey: "file_size",
    header: "文件大小",
  },
]

export const LibraryDetail = () => {
  const {id} = useParams<{id: string}>()
  const { data, error, isLoading, mutate } = useSWR<MaxKbDocument[]>(FetchDocumentApi({dataset_id: id}), () => fetch(FetchDocumentApi({dataset_id: id})).then(r => r.json()))
  const table = useReactTable({
    data: data || [],
    columns,
    getRowId: row => `${row.id}`,
    getCoreRowModel: getCoreRowModel(),
  })
  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div className="flex-1 p-2">
      <div>
        <Link to={`/library/detail/${id}/document/create`}>
          <Button>Create</Button>
        </Link>
        <Button onClick={async () => {
          const ids = table.getSelectedRowModel().rows.map(r => r.id)
          await fetch(DeleteDocumentApi({dataset_id: id}), {
            method: "DELETE",
            body: JSON.stringify(ids),
            headers: {
              'Content-Type': 'application/json'
            }
          })
          mutate()
        }}>Delete</Button>
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
    </div>
  )
}
