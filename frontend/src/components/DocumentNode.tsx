import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { FileText, Hash, Calendar } from 'lucide-react';

interface DocumentNodeData {
  label: string;
  fullText: string;
  similarity: number;
  metadata: {
    source_page_id: string;
    block_type: string;
    page_title_path: string[];
    active_headings: string[];
  };
}

interface DocumentNodeProps {
  data: DocumentNodeData;
}

const DocumentNode = memo(({ data }: DocumentNodeProps) => {
  const { label, fullText, similarity, metadata } = data;
  
  return (
    <div className="bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 rounded-lg p-4 shadow-lg min-w-[250px] max-w-[350px]">
      <Handle type="target" position={Position.Top} className="w-3 h-3" />
      
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <FileText className="w-4 h-4 text-blue-500" />
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
          {metadata.block_type}
        </span>
        <div className="ml-auto bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded-full text-xs font-medium">
          {(similarity * 100).toFixed(1)}%
        </div>
      </div>
      
      {/* Content */}
      <div className="mb-3">
        <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
          {label}
        </p>
      </div>
      
      {/* Metadata */}
      <div className="space-y-2 text-xs text-slate-500 dark:text-slate-400">
        {metadata.page_title_path.length > 0 && (
          <div className="flex items-start gap-2">
            <Hash className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <div className="truncate">
              {metadata.page_title_path.join(' > ')}
            </div>
          </div>
        )}
        
        {metadata.active_headings.length > 0 && (
          <div className="flex items-start gap-2">
            <FileText className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <div className="truncate">
              {metadata.active_headings.join(' > ')}
            </div>
          </div>
        )}
      </div>
      
      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  );
});

DocumentNode.displayName = 'DocumentNode';

export default DocumentNode; 