import { useState, useCallback, useMemo, useEffect } from 'react';
import { ReactFlow, Node, Edge, addEdge, useNodesState, useEdgesState, Background, Controls, NodeTypes } from '@xyflow/react';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { SearchIcon, RefreshCwIcon } from 'lucide-react';
import DocumentNode from '@/components/DocumentNode';
import ThemeToggle from '@/components/ThemeToggle';
import '@xyflow/react/dist/style.css';

const SIMILARITY_THRESHOLD = 0.01;

interface SearchResult {
  id: string;
  document: string;
  similarity_score: number;
  metadata: {
    source_page_id: string;
    block_type: string;
    page_title_path: string[];
    active_headings: string[];
  };
}

interface SearchResponse {
  success: boolean;
  message: string;
  results: SearchResult[];
}

export default function IndexPage() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [existingNodes, setExistingNodes] = useState<Set<string>>(new Set());

  // useEffect(() => {
  //   console.log(edges);
  // }, [edges]);

  // useEffect(() => {
  //   console.log(nodes);
  // }, [nodes]);

  const nodeTypes = useMemo<NodeTypes>(() => ({
    documentNode: DocumentNode,
  }), []);

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    try {
      const response = await fetch('http://localhost:8001/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          top_k: 3
        }),
      });

      const data: SearchResponse = await response.json();

      if (data.success && data.results) {
        // Add new nodes for search results
        const newNodes: Node[] = [];
        const newEdges: Edge[] = [];
        const newExistingNodes = new Set(existingNodes);

        data.results.forEach((result, index) => {
          if (!existingNodes.has(result.id)) {
            const newNode: Node = {
              id: result.id,
              type: 'documentNode',
              position: {
                x: 250 + (index * 200),
                y: 100 + (index * 150)
              },
              data: {
                label: result.document.substring(0, 100) + (result.document.length > 100 ? '...' : ''),
                fullText: result.document,
                similarity: result.similarity_score,
                metadata: result.metadata
              },
                             style: {
                 background: 'transparent',
                 border: 'none',
                 padding: '0'
               }
            };
            newNodes.push(newNode);
            newExistingNodes.add(result.id);
          }
        });

          // Create edges between new nodes based on similarity
         for (let i = 0; i < newNodes.length; i++) {
           for (let j = i + 1; j < newNodes.length; j++) {
             const node1 = newNodes[i];
             const node2 = newNodes[j];
             // Use average similarity as edge strength
             const similarity = (Number(node1.data.similarity) + Number(node2.data.similarity)) / 2;
             if (Math.abs(similarity) > SIMILARITY_THRESHOLD) {
               const edge: Edge = {
                 id: `e${node1.id}-${node2.id}-${Date.now()}-${Math.random()}`,
                 source: node1.id,
                 target: node2.id,
                 type: 'step',
                 label: `${(similarity * 100).toFixed(1)}%`,
                 style: {
                   stroke: `hsl(${200 + (similarity * 60)}, 70%, 50%)`,
                   strokeWidth: Math.max(2, similarity * 8)
                 },
                 labelStyle: {
                   fill: '#374151',
                   fontSize: '12px',
                   fontWeight: '600'
                 },
                 labelBgStyle: {
                   fill: 'white',
                   fillOpacity: 0.8
                 }
               };
               newEdges.push(edge);
             }
           }
         }

        // Connect new nodes to existing nodes
         nodes.forEach(existingNode => {
           newNodes.forEach(newNode => {
             // Use average similarity as edge strength
             const similarity = (Number(existingNode.data.similarity) + Number(newNode.data.similarity)) / 2;
             if (similarity > SIMILARITY_THRESHOLD) {
               const edge: Edge = {
                 id: `e${existingNode.id}-${newNode.id}-${Date.now()}-${Math.random()}`,
                 source: existingNode.id,
                 target: newNode.id,
                 type: 'default',
                 label: `${(similarity * 100).toFixed(1)}%`,
                 style: {
                   stroke: `hsl(${200 + (similarity * 60)}, 70%, 50%)`,
                   strokeWidth: Math.max(2, similarity * 8)
                 },
                 labelStyle: {
                   fill: '#374151',
                   fontSize: '12px',
                   fontWeight: '600'
                 },
                 labelBgStyle: {
                   fill: 'white',
                   fillOpacity: 0.8
                 }
               };
               newEdges.push(edge);
             }
           });
         });

        setNodes(prev => [...prev, ...newNodes]);
        setEdges(prev => [...prev, ...newEdges]);
        setExistingNodes(newExistingNodes);
        
        // Debug logging
        console.log('New nodes created:', newNodes.length);
        console.log('New edges created:', newEdges.length);
        console.log('Total edges now:', edges.length + newEdges.length);
        console.log('Sample edge:', newEdges[0]);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  }, [query, existingNodes, nodes]);

  const handleReset = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setExistingNodes(new Set());
    setHasSearched(false);
    setQuery('');
  }, [setNodes, setEdges]);

  const handleTestEdge = useCallback(() => {
    // Create test nodes and edge
    const testNode1: Node = {
      id: 'test-node-1',
      type: 'documentNode',
      position: { x: 100, y: 100 },
      data: {
        label: 'Test Node 1',
        fullText: 'This is a test node',
        similarity: 0.8,
        metadata: {
          source_page_id: 'test1',
          block_type: 'test',
          page_title_path: ['Test'],
          active_headings: ['Test Heading']
        }
      }
    };
    
    const testNode2: Node = {
      id: 'test-node-2',
      type: 'documentNode',
      position: { x: 400, y: 400 },
      data: {
        label: 'Test Node 2',
        fullText: 'This is another test node',
        similarity: 0.7,
        metadata: {
          source_page_id: 'test2',
          block_type: 'test',
          page_title_path: ['Test'],
          active_headings: ['Test Heading']
        }
      }
    };
    
    const testEdge: Edge = {
      id: 'test-edge-1',
      source: 'test-node-1',
      target: 'test-node-2',
      type: 'default',
      label: '75%',
      style: {
        stroke: '#3B82F6',
        strokeWidth: 3
      },
      labelStyle: {
        fill: '#374151',
        fontSize: '12px',
        fontWeight: '600'
      },
      labelBgStyle: {
        fill: 'white',
        fillOpacity: 0.8
      }
    };
    
    setNodes([testNode1, testNode2]);
    setEdges([testEdge]);
    setHasSearched(true);
    console.log('Test nodes and edge created:', { nodes: [testNode1, testNode2], edge: testEdge });
  }, [setNodes, setEdges]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isSearching) {
      handleSearch();
    }
  }, [handleSearch, isSearching]);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <ThemeToggle />
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-800 dark:text-slate-200 mb-2">
            Semantic Search Graph
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Explore document relationships through semantic similarity
          </p>
        </div>

        {/* Search Input */}
        <div className={`transition-all duration-500 ease-in-out ${
          hasSearched ? 'mb-6' : 'mb-16'
        }`}>
          <div className={`max-w-2xl mx-auto ${
            hasSearched ? 'w-full' : 'w-full'
          }`}>
            <div className="flex gap-2">
              <Input
                type="text"
                placeholder="What would you like to search for today?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
                size="lg"
                startContent={<SearchIcon className="w-5 h-5 text-slate-400" />}
                disabled={isSearching}
              />
              <Button
                color="primary"
                size="lg"
                onClick={handleSearch}
                isLoading={isSearching}
                disabled={!query.trim()}
              >
                Search
              </Button>
              {hasSearched && (
                <Button
                  variant="bordered"
                  size="lg"
                  onClick={handleReset}
                  startContent={<RefreshCwIcon className="w-4 h-4" />}
                >
                  Reset
                </Button>
              )}
              <Button
                variant="bordered"
                size="lg"
                onClick={handleTestEdge}
                className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
              >
                Test Edge
              </Button>
            </div>
          </div>
        </div>

        {/* Graph View */}
        {hasSearched && (
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700">
            <div className="h-[600px] w-full">
              <ReactFlow
                 nodes={nodes}
                 edges={edges}
                 nodeTypes={nodeTypes}
                //  onNodesChange={onNodesChange}
                //  onEdgesChange={onEdgesChange}
                //  onConnect={onConnect}
                 fitView
                //  attributionPosition="bottom-left"
                //  defaultEdgeOptions={{
                //    style: {
                //      stroke: '#93C5FD',
                //      strokeWidth: 2,
                //    },
                //    labelStyle: {
                //      fill: '#374151',
                //      fontSize: '12px',
                //      fontWeight: '600',
                //    },
                //    labelBgStyle: {
                //      fill: 'white',
                //      fillOpacity: 0.8,
                //    },
                //  }}
               >
                <Background />
                <Controls />
              </ReactFlow>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
