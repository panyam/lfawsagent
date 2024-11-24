import faiss, ipdb
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer
import numpy as np

class VectorStore:
    def __init__(self):
        print("Loading embedding model....")
        # Load the SentenceTransformer model for embedding
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and efficient

        # Initialize the FAISS index
        print("Initializing FAISS Index....")
        self.index = faiss.IndexFlatL2(self.embedding_model.get_sentence_embedding_dimension())
        self.tool_embeddings = []  # To store embeddings
        self.tools = []

    def add_tools(self, tools):
        """Build an in-memory vector store for tool descriptions."""
        # Embed tool descriptions
        print(f"Adding {len(tools)} tools...")
        descriptions = [f"{tool['name']}: {tool['description']}" for tool in tools]

        embeddings = []
        batch_size = 1000
        if True:
            for i in range(0, len(descriptions), batch_size):
                print("Processing Batch: ", i)
                batch = descriptions[i:i + batch_size]
                batch_embeddings = self.embedding_model.encode(batch, convert_to_numpy=True)
                embeddings.extend(batch_embeddings)
        else:
            for tool in tools:
                description = f"{tool['name']}: {tool['description']}"
                print("Adding Tool: ", description)
                self.tool_descriptions.append(tool)  # Store full tool details
                embedding = self.embedding_model.encode(description, convert_to_numpy=True)
                embeddings.append(embedding)

        # Add embeddings to the FAISS index
        self.tools.extend(tools)
        self.tool_embeddings.append(embeddings)
        self.index.add(np.array(embeddings))

    def retrieve_relevant_tools(self, query, top_n=5):
        """Retrieve the top N relevant tools for a user query."""
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        distances, indices = self.index.search(query_embedding.reshape(1, -1), top_n)

        # Get the closest tools
        relevant_tools = [self.tools[i] for i in indices[0]]
        return relevant_tools


    def prompt_for_query_with_tools(self, user_query, top_n=5):
        """Parse user query and select the appropriate tool using Mistral."""
        relevant_tools = self.retrieve_relevant_tools(user_query, top_n)
        tools_description = "\n".join(
            f"- Tool: {tool['name']}\n  Description: {tool['description']}\n  Parameters: {tool['parameters']}"
            for tool in relevant_tools
        )

        prompt = f"""
You are an intelligent assistant for AWS cloud management. Your task is to interpret the user's query and select the most appropriate tool from the following list:

{tools_description}

User Query: "{user_query}"

Return a JSON object with:
- tool: The name of the tool to use.
- parameters: The parameters required for the selected tool.
"""
        return prompt
