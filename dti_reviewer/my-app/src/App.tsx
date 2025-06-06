import { useState, type ChangeEvent } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { ResultTable } from "./components/ResultTable"
import logo from "./assets/logo.png";
import Search  from "./assets/search.svg"
import NoResults from "./assets/noResults.png"

function App() {
  const [query, setQuery] = useState("")
  const [tableData, setTableData] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleQuery = (e: ChangeEvent<HTMLTextAreaElement>): void => {
    setQuery(e.target.value)
  }

  const fetchData = async () => {
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    return data
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    setLoading(true)
    try {
      setHasSearched(true)
      const data = await fetchData()
      setTableData(data.results)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="w-4/5 m-auto grid grid-cols-5 gap-3">
        {/*Row 1*/}
        <div className="col-span-5 flex items-center justify-center">
          <img id="logo" className="animate-wiggle animate-infinite" src={logo} />
          <h1 className="font-bold text-center">Expert Finder</h1>
        </div>

        {/*Row 2*/}
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 border-none shadow-lg rounded-lg md:gap-4 col-span-5">
          <div className="md:col-span-4 pt-6 pr-6 pl-6 pb-0 md:pb-6 md:pr-0">
            <p>Enter your abstract</p>
            <Textarea
              placeholder="Enter your text here..."
              value={query}
              onChange={handleQuery}
              className="w-full min-h-[80px] md:min-h-[100px] resize-y"
              required
            />
          </div>
          <div className="md:col-span-1 flex flex-col justify-end p-6 md:pl-0">
            <Button
              type="submit"
              disabled={loading}
              className={`w-full
                     ${loading ? "bg-gray-400 cursor-not-allowed" : "bg-primary hover:bg-primary/90"}`}
            >
              {loading ? (
                <span>
                  Searching…</span>)
                :
                <span>Search</span>
              }
            </Button>
          </div>
        </form>

        {/*Row 3*/}
        <div className="col-span-5 border-none rounded-lg shadow-lg">
          <div className="pl-4">
            <h2>Search Results</h2>
          </div>
          <div className="overflow-y-auto h-[50vh] max-h-[60vh]">
            {loading ? (
              <div className="flex flex-col items-center justify-center h-full">
                <div
                  className="
                  animate-spin 
                  h-30 w-30 
                  border-4 
                  border-primary
                  border-t-transparent 
                  rounded-full
                "
                />
                <p className="text-lg">
                  Searching for experts...
                </p>
              </div>

            ) : !hasSearched ? (
              <div className="h-full flex flex-col items-center justify-center text-stone-500 p-12">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br bg-stone-400 flex items-center justify-center mb-4">
                  <img src={Search} alt="Search icon" className="w-10 h-10" />
                </div>
                <p className="text-xl font-semibold mb-2">Ready to explore</p>
                <p className="text-base text-stone-400">
                  Enter your paragraph above to begin analysis
                </p>
      
              </div>
              
            ) : tableData.length === 0 ? (
              <>
              <img src={NoResults} alt="No results" className="w-20 h-20 mx-auto mb-4" />
              <p className="text-center text-lg">No results</p>
              </>
            ) : (
              <div className="pt-0 p-4 rouded-lg ">
                <ResultTable dataToDisplay={tableData} />
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default App;
