
import { useState } from 'react';
import { Text, Music, FileVideo, Layers, Captions, Templates, Video } from 'lucide-react';
import { cn } from '@/lib/utils';
import { AssetItem, assetTabs } from '@/config/assetsConfig';
import { useToast } from '@/hooks/use-toast';

const AssetsIconBar = () => {
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const { toast } = useToast();

  const handleIconClick = (tabId: string) => {
    setActiveTab(prevTab => prevTab === tabId ? null : tabId);
  };

  const handleDragStart = (e: React.DragEvent, asset: AssetItem) => {
    e.dataTransfer.setData('application/json', JSON.stringify({
      type: 'ASSET',
      asset
    }));
    e.dataTransfer.effectAllowed = 'copy';
  };

  const getTabItems = (tabId: string) => {
    const tab = assetTabs.find(t => t.id === tabId);
    return tab ? tab.items : [];
  };

  const tabIcons = [
    { id: 'video', name: 'Video', icon: Video },
    { id: 'text', name: 'Text', icon: Text },
    { id: 'sounds', name: 'Sounds', icon: Music },
    { id: 'media', name: 'Media', icon: FileVideo },
    { id: 'captions', name: 'Captions', icon: Captions },
    { id: 'layers', name: 'Layers', icon: Layers },
    { id: 'templates', name: 'Templates', icon: Templates }
  ];

  return (
    <div className="flex h-full">
      {/* Vertical Icon Bar */}
      <div className="bg-cre8r-gray-800 border-r border-cre8r-gray-700 w-14 flex flex-col items-center py-4 space-y-6">
        {tabIcons.map(tab => (
          <button
            key={tab.id}
            onClick={() => handleIconClick(tab.id)}
            className={cn(
              "w-10 flex flex-col items-center gap-1 transition-colors",
              activeTab === tab.id 
                ? "text-white" 
                : "text-cre8r-gray-400 hover:text-white"
            )}
            title={tab.name}
          >
            <div className={cn(
              "h-10 w-10 rounded-md flex items-center justify-center",
              activeTab === tab.id 
                ? "bg-cre8r-violet" 
                : "hover:bg-cre8r-gray-700"
            )}>
              <tab.icon className="h-5 w-5" />
            </div>
            <span className="text-[10px] hidden sm:block">
              {tab.name}
            </span>
          </button>
        ))}
      </div>

      {/* Asset Items Panel - shown when a tab is active */}
      {activeTab && (
        <div className="bg-cre8r-gray-800 w-64 overflow-y-auto">
          <div className="p-4 border-b border-cre8r-gray-700">
            <h3 className="font-medium text-white">
              {tabIcons.find(tab => tab.id === activeTab)?.name}
            </h3>
          </div>
          <div className="p-2 space-y-1">
            {getTabItems(activeTab).map(item => (
              <div 
                key={item.id}
                className="group flex items-center p-2 rounded hover:bg-cre8r-gray-700 cursor-grab transition-colors"
                draggable
                onDragStart={(e) => handleDragStart(e, item)}
              >
                {item.thumbnail ? (
                  <div className="h-10 w-10 mr-3 bg-cre8r-gray-700 rounded overflow-hidden flex-shrink-0">
                    <img 
                      src={item.thumbnail} 
                      alt={item.name} 
                      className="h-full w-full object-cover"
                    />
                  </div>
                ) : (
                  <div className={cn(
                    "h-8 w-8 mr-3 rounded flex items-center justify-center flex-shrink-0",
                    item.type === 'text' ? "bg-blue-600" : 
                    item.type === 'audio' ? "bg-purple-600" : "bg-green-600"
                  )}>
                    <span className="text-xs font-bold text-white">
                      {item.type === 'text' ? 'T' : 
                       item.type === 'audio' ? 'A' : 'V'}
                    </span>
                  </div>
                )}
                <span className="text-sm truncate">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetsIconBar;
