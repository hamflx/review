import { ChatApi } from "@/apis/chat"
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
import { useCallback, useState } from "react"
import { FetchDatasetApi, MaxKbDataset } from "@/apis/files"
import useSWR from "swr"

const formSchema = z.object({
  query: z.string().min(1).max(500),
})

interface MessageModel {
  message: string
  role: 'assistant' | 'user'
}

export const Search = () => {
  const { data: datasetList } = useSWR<MaxKbDataset[]>(FetchDatasetApi, () => fetch(FetchDatasetApi).then(r => r.json()))
  const [selectedDatasetId, setSelectedDatasetId] = useState('0')

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: ''
    },
  })

  const [historyMessages, setHistoryMessages] = useState<MessageModel[]>([])
  const appendLastMessage = (msg: string) => setHistoryMessages(historyMessages => {
    console.log('append', msg)
    const copy = historyMessages.map(m => ({...m}))
    let lastAssistantMsg = copy[copy.length - 1]
    if (!lastAssistantMsg || lastAssistantMsg.role === 'user') {
      lastAssistantMsg = {message: '', role: 'assistant'}
      copy.push(lastAssistantMsg)
    }
    lastAssistantMsg.message += msg
    return copy
  })

  const onSubmitForm = async (values: z.infer<typeof formSchema>) => {
    const newMessage = {
      message: values.query,
      role: 'user',
    } as const
    setHistoryMessages([...historyMessages, newMessage])
    const params = {
      ...values,
      datasetId: selectedDatasetId,
      history: historyMessages,
    }
    const response = await fetch(ChatApi, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    })
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    while (true) {
      const {done, value} = (await reader?.read()) ?? {}
      if (done) {
        break
      }
      appendLastMessage(decoder.decode(value))
    }
  }
  const lastMessage = useCallback((element: HTMLDivElement) => {
    if (element) {
      element.scrollIntoView()
    }
  }, [])
  return (
    <Card className="flex flex-col flex-1 m-2 ml-0">
      <CardHeader>
        <CardTitle>AI 检索</CardTitle>
        <CardDescription>
          <Label>在您选择的知识库中检索需要的内容。</Label>
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-4 overflow-auto">
        {historyMessages.map((m, index) => {
          return (
            <div ref={index+1 === historyMessages.length ? lastMessage : null} key={index} className={`space-y-2 flex flex-col ${m.role === 'user' ? 'place-self-end items-end' : 'place-self-start items-start'}`}>
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
          <Select defaultValue={selectedDatasetId} onValueChange={datasetId => setSelectedDatasetId(datasetId)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="选择知识库" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="0">全部</SelectItem>
              {
                (datasetList || []).map(dataset => {
                  return (
                    <SelectItem value={dataset.id} key={dataset.id}>{dataset.name}</SelectItem>
                  )
                })
              }
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
