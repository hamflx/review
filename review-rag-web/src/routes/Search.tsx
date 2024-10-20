import { ChatApi, ChatResponse } from "@/apis/chat"
import { CommonResponse, isError } from "@/apis/common"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { useState } from "react"

const formSchema = z.object({
  query: z.string().min(1).max(500),
})

interface MessageModel {
  message: string
  role: 'assistant' | 'user'
}

export const Search = () => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: ''
    },
  })

  const [historyMessages, setHistoryMessages] = useState<MessageModel[]>([])

  const onSubmitForm = async (values: z.infer<typeof formSchema>) => {
    const newMessage = {
      message: values.query,
      role: 'user',
    } as const
    setHistoryMessages([...historyMessages, newMessage])
    const response: CommonResponse<ChatResponse> = await fetch(ChatApi, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(values),
    }).then(r => r.json())
    if (isError(response)) {
      alert(response.error)
    } else {
      setHistoryMessages([...historyMessages, newMessage, {message: response.message, role: 'assistant'}])
    }
  }
  return (
    <Card className="flex flex-col flex-1 m-2 ml-0">
      <CardHeader>
        <CardTitle>AI 检索</CardTitle>
        <CardDescription>
          <Label>在您选择的知识库中检索需要的内容。</Label>
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4">
        {historyMessages.map(m => {
          return (
            <div className={`space-y-2 ${m.role === 'user' ? 'place-self-end' : 'place-self-start'}`}>
              <Label>{m.role}</Label>
              <Card>
                <CardContent className="flex-1 p-2">
                  <div>{m.message}</div>
                </CardContent>
              </Card>
            </div>
          )
        })}
      </CardContent>
      <CardFooter className="flex-col items-start gap-4">
        <div className="flex flex-col gap-4">
          <Label>选择知识库</Label>
          <Select>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Theme" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="light">Light</SelectItem>
              <SelectItem value="dark">Dark</SelectItem>
              <SelectItem value="system">System</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Form {...form}>
          <form className="flex w-full items-end flex-1 gap-2" onSubmit={form.handleSubmit(onSubmitForm)}>
            <FormField
              control={form.control}
              name="query"
              render={({field}) => (
                <FormItem className="flex-1">
                  <FormMessage />
                  <FormControl>
                    <Input {...field}/>
                  </FormControl>
                </FormItem>
              )}
            />
            <Button type="submit">发送</Button>
          </form>
        </Form>
      </CardFooter>
    </Card>
  )
}
