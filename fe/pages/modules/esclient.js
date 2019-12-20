import { Client } from "elasticsearch"

const host = "localhost:9200"

export default new Client({ host });