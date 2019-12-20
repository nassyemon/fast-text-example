const HIGHLIGHT_PRE_TAG = "<em>";
const HIGHLIGHT_POST_TAG = "</em>";


const spanRegex = () =>
  new RegExp(`(${HIGHLIGHT_PRE_TAG}.*?${HIGHLIGHT_POST_TAG})`, "gi");


export default text => {
  const flagged = text
    .split(spanRegex())
    .filter(chunk => chunk.length > 0)
    .map(chunk => {
      if (spanRegex().test(chunk)) {
        return [
          chunk.replace(HIGHLIGHT_PRE_TAG, "").replace(HIGHLIGHT_POST_TAG, ""),
          true,
        ];
      }
      return [chunk, false];
    });
  return flagged;
};