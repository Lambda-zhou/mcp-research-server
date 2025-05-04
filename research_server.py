import arxiv
import json
import os
from typing import List, Dict, Any, Optional
import PyPDF2
from fastmcp import FastMCP


PAPER_DIR = "papers"

# Initialize FastMCP server for research papers
mcp = FastMCP("research-papers")

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.
    
    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)
        
    Returns:
        List of paper IDs found in the search
    """
    
    # Use arxiv to find the papers 
    client = arxiv.Client()

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query = topic,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)
    
    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    
    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info  
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            'title': paper.title,
            'authors': [author.name for author in paper.authors],
            'summary': paper.summary,
            'pdf_url': paper.pdf_url,
            'published': str(paper.published.date())
        }
        papers_info[paper.get_short_id()] = paper_info
    
    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)
    
    print(f"Results are saved in: {file_path}")
    
    return paper_ids

@mcp.tool()
def extract_info(paper_id: str) -> Optional[str]:
    """
    Search for information about a specific paper across all topic directories.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """
 
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue
    
    return f"There's no saved information related to paper {paper_id}."

@mcp.tool()
def extract_text_paper(paper_path: str) -> Optional[str]:
    """
    Extract text content from a PDF file and save it as a text file.
    
    Args:
        paper_path: Path to the PDF file to extract text from
        
    Returns:
        Path to the output text file if successful, None otherwise
    """
    try:
        # Check if file exists
        if not os.path.isfile(paper_path):
            print(f"Error: File {paper_path} does not exist")
            return None
            
        total_text = ""
        
        # Open and read the PDF
        with open(paper_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            total_pages = len(reader.pages)
            
            print(f"Extracting text from {paper_path} ({total_pages} pages)")
            
            # Extract text from each page
            for page_num in range(total_pages):
                    
                # Get the page
                page = reader.pages[page_num]
                
                # Extract text from the page
                page_text = page.extract_text()
                
                # Add the page text to the overall text
                if page_text:
                    total_text += page_text + "\n\n"
        
        # Create the output file path (same directory, .txt extension)
        output_path = os.path.splitext(paper_path)[0] + '.txt'
        
        # Write the extracted text to the output file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(total_text)
            
        print(f"Text extraction complete. Results saved in: {output_path}")
        return output_path
        
    except PyPDF2.errors.PdfReadError:
        print(f"Error: The file {paper_path} appears to be corrupted or not a valid PDF")
        return None


if __name__ == "__main__":
    mcp.run(transport="sse")