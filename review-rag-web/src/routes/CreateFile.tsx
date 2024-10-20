import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useForm } from "react-hook-form"
import { Form, FormField, FormLabel, FormControl, FormDescription, FormMessage, FormItem } from "@/components/ui/form"
import { CreateFileApi } from "@/apis/files"
import { ChangeEventHandler, useState } from "react"
import { useNavigate } from "react-router-dom";
import { CommonResponse, errorMessage } from "@/apis/common"

// 最大允许上传 5MB 文件。
const MEGA_BYTES = 1024 * 1024
const MAX_FILE_SIZE = 5 * MEGA_BYTES

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
  const navigate = useNavigate()
  async function onSubmit() {
    const formData = new FormData()
    if (fileObject) {
      if (fileObject.size > MAX_FILE_SIZE) {
        form.setError('file', {message: `最大支持 ${MAX_FILE_SIZE / MEGA_BYTES}MB 的文件`})
        return
      }
      formData.append('file', fileObject)
      const response: CommonResponse<unknown> = await fetch(CreateFileApi, {
        method: 'POST',
        body: formData
      }).then(r => r.json())
      const error = errorMessage(response)
      if (error) {
        alert(error)
      } else {
        navigate('/file/list')
      }
    } else {
      form.setError('file', {message: '请选择文件'})
    }
  }
  return (
    <div className="p-2">
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
                  This is your public display name.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit">提交</Button>
        </form>
      </Form>
    </div>
  )
}
