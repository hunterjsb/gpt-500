# GPT20 Index Update Task

You are updating the GPT20 index using the provided tools. Follow these steps exactly:

## Step 1: Read Current Index

Use the `read_index` tool with parameter `index_name: "GPT20"` to read the current index file.

If the tool fails or returns an error, explain what went wrong and stop.

## Step 2: Get Current Time

Use the `current_time` tool to get the current timestamp for the update.

If the tool fails or returns an error, explain what went wrong and stop.

## Step 3: Analyze and Update

Based on the current index content, analyze:

- Market performance since last update
- Economic indicators and sector trends
- Individual stock fundamentals
- Portfolio diversification
- Better opportunities available

Make decisions about which stocks to keep, remove, or add.

## Step 4: Write Updated Index

Use the `write_index` tool with parameters:

- `index_name: "GPT20"`
- `content: [your complete markdown content]`

The content must include:

- Header explaining GPT20 purpose
- Exactly 20 stocks in numbered list format
- Brief rationale for each stock
- Current timestamp from Step 2
- Summary of any changes made

If the write_index tool fails, explain what went wrong and try again with corrected content.

## Error Handling

If any tool call fails:

1. Report the specific error
2. Explain what you were trying to do
3. If possible, suggest what might be wrong
4. Do not proceed to the next step until the current step succeeds

## Success Confirmation

After successfully writing the index, confirm:

- Which tool calls were made
- What changes were made to the index
- The file was written successfully

You MUST use the tools - do not output file content directly.
