import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useForm } from "react-hook-form"
import { Form, FormField, FormLabel, FormControl, FormDescription, FormMessage, FormItem } from "@/components/ui/form"
import { CreateDatasetApi, MaxKbDataset } from "@/apis/files"
import { CommonResponse, errorMessage } from "@/apis/common"
import { z } from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { useNavigate } from "react-router-dom"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

const formSchema = z.object({
  name: z.string().min(2).max(50),
  description: z.string().max(500),
})

export const CreateLibray = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      description: '',
    },
  })
  const navigate = useNavigate()
  // 2. Define a submit handler.
  async function onSubmit(values: z.infer<typeof formSchema>) {
    const response: CommonResponse<MaxKbDataset> = await fetch(CreateDatasetApi, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    }).then(r => r.json())
    const error = errorMessage(response)
    if (error) {
      alert(error)
    } else {
      navigate('/library/list')
    }
  }
  return (
    <Card className="flex flex-col flex-1 m-2 ml-0 overflow-hidden">
      <CardHeader>
        <CardTitle>知识库管理</CardTitle>
        <CardDescription>您可以创建多个知识库，在与 AI 对话时，可以选择知识库上下文。</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-1">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 flex-1">
            <FormField
              control={form.control}
              name="name"
              render={({field}) => (
                <FormItem>
                  <FormLabel>知识库名称</FormLabel>
                  <FormControl>
                    <Input {...field}/>
                  </FormControl>
                  <FormDescription>
                    This is your public display name.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({field}) => (
                <FormItem>
                  <FormLabel>知识库描述</FormLabel>
                  <FormControl>
                    <Input {...field}/>
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
      </CardContent>
    </Card>
  )
}
