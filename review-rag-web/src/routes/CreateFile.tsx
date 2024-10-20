import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useForm } from "react-hook-form"
import { Form, FormField, FormLabel, FormControl, FormDescription, FormMessage, FormItem } from "@/components/ui/form"
import { CreateDocumentApi } from "@/apis/files"
import { ChangeEventHandler, useState } from "react"
import { useNavigate, useParams } from "react-router-dom";
import { CommonResponse, errorMessage } from "@/apis/common"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

// 最大允许上传 30MB 文件。
const MEGA_BYTES = 1024 * 1024
const MAX_FILE_SIZE = 30 * MEGA_BYTES

export const CreateFile = () => {
  const form = useForm({
    defaultValues: {
      file: {}
    }
  })
  const [fileObject, setFileObject] = useState<File | undefined>(undefined)
  const onFileChange: ChangeEventHandler<HTMLInputElement> = (event) => {
    setFileObject(event.target.files?.[0])
    form.clearErrors()
  }
  const {id} = useParams()
  const navigate = useNavigate()
  async function onSubmit() {
    const formData = new FormData()
    if (fileObject) {
      if (fileObject.size > MAX_FILE_SIZE) {
        form.setError('file', {message: `最大支持 ${MAX_FILE_SIZE / MEGA_BYTES}MB 的文件`})
        return
      }
      formData.append('file', fileObject)
      const response: CommonResponse<unknown> = await fetch(CreateDocumentApi({dataset_id: id}), {
        method: 'POST',
        body: formData
      }).then(r => r.json())
      const error = errorMessage(response)
      if (error) {
        alert(error)
      } else {
        navigate(`/library/detail/${id}/document/list`)
      }
    } else {
      form.setError('file', {message: '请选择文件'})
    }
  }
  return (
    <Card className="flex flex-col flex-1 m-2 ml-0 overflow-hidden">
      <CardHeader>
        <CardTitle>上传文档</CardTitle>
        <CardDescription>选择 PDF 文件上传，上传后会自动开始向量化。</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="file"
              render={() => (
                <FormItem>
                  <FormLabel>文件</FormLabel>
                  <FormControl>
                    <Input type="file" onChange={onFileChange}/>
                  </FormControl>
                  <FormDescription>
                    目前仅支持 PDF，且文件大小应在 30MB 以内。另外 vercel 部署会限制到 4.5MB。
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit">提交</Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
