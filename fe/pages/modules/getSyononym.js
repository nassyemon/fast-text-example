import fetch from "node-fetch";
import qs from "query-string";

const baseUrl = "http://localhost:5000/synonyms/search"
export default async (term) => {
  const params = qs.stringify({ q: term })
  const url = `${baseUrl}?${params}`
  const ret = await fetch(url);
  const response = await ret.json();
  if (!response || !Array.isArray(response.results)) {
    return null;
  }
  const { results } = response;
  if(results.length < 0) {
      return null;
  }
  return results.map(({ i, word }) => ({ i, word }));
}