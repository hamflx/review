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
import { useRef, useState } from "react"
import { FetchDatasetApi, MaxKbDataset } from "@/apis/files"
import useSWR from "swr"
import Markdown from 'react-markdown'

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
  const [chatPending, setChatPending] = useState(false)

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: ''
    },
  })

  const [historyMessages, setHistoryMessages] = useState<MessageModel[]>([])
  const appendLastMessage = (msg: string) => setHistoryMessages(historyMessages => {
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
    setChatPending(true)
    form.reset()
    try {
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
        scrollIfNeeded()
      }
    } finally {
      setChatPending(false)
    }
  }
  const scrollContainer = useRef<HTMLDivElement | null>(null)
  // 自动滚动容器，避免新出现的文字看不见，自动将其滚动到可视区域。
  // 同时，为了避免自动滚动导致用户无法锚定一个位置，这里仅在滚动位置靠近底部的时候启用。
  const scrollIfNeeded = () => {
    const el = scrollContainer.current
    const threshold = 50
    if (el) {
      if (el.scrollHeight - (el.scrollTop + el.offsetHeight) <= threshold) {
        setTimeout(() => {
          el.scrollTop = el.scrollHeight - el.offsetHeight
        })
      }
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
      <CardContent ref={scrollContainer} className="flex-1 flex flex-col gap-4 overflow-auto">
        {historyMessages.map((m, index) => {
          return (
            <div key={index} className={`space-y-2 flex flex-col ${m.role === 'user' ? 'place-self-end items-end' : 'place-self-start items-start'}`}>
              <Label>{m.role}</Label>
              <Card>
                <CardContent className="flex-1 py-2 px-4">
                  <Markdown className="markdown-container unreset">{m.message}</Markdown>
                </CardContent>
              </Card>
            </div>
          )
        })}
      </CardContent>
      <CardFooter className="flex-col items-start gap-4">
        {chatPending && <Label className="place-self-center">正在生成……</Label>}
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
            <Button type="submit" disabled={chatPending}>发送</Button>
          </form>
        </Form>
      </CardFooter>
    </Card>
  )
}
