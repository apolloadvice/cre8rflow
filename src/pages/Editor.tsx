
import { useState, useEffect, useRef } from "react";
import { useToast } from "@/hooks/use-toast";
import NavBar from "@/components/NavBar";
import AssetPanel from "@/components/editor/AssetPanel";
import AssetsIconBar from "@/components/editor/AssetsIconBar";
import VideoPlayer from "@/components/editor/VideoPlayer";
import Timeline from "@/components/editor/Timeline";
import ChatPanel from "@/components/editor/ChatPanel";
import TimecodeDisplay from "@/components/editor/TimecodeDisplay";
import { Button } from "@/components/ui/button";
import { Save, Film } from "lucide-react";
import UndoIcon from "@/components/icons/UndoIcon";
import RedoIcon from "@/components/icons/RedoIcon";
import { ResizablePanel, ResizablePanelGroup, ResizableHandle } from "@/components/ui/resizable";
import { useThumbnails } from "@/hooks/useThumbnails";
import { useCommand, Operation } from "@/hooks/useCommand";
import { 
  useEditorStore,
  useKeyboardShortcuts,
  useLayout,
  useLayoutSetter,
  Clip
} from "@/store/editorStore";

const Editor = () => {
  const { toast } = useToast();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const timelineRef = useRef<HTMLDivElement | null>(null);
  
  // Get layout state and setter
  const layout = useLayout();
  const setLayoutSize = useLayoutSetter();
  
  // Get state and actions from our store
  const {
    clips, 
    currentTime, 
    duration, 
    selectedClipId,
    activeVideoAsset,
    videoSrc,
    setClips,
    setCurrentTime,
    setDuration,
    setSelectedClipId,
    setActiveVideoAsset,
    setVideoSrc,
    undo,
    redo,
    history
  } = useEditorStore();
  
  // Setup keyboard shortcuts
  useKeyboardShortcuts();
  
  // Integrate our hooks
  const { thumbnailData } = useThumbnails(activeVideoAsset?.id);
  const { executeCommand } = useCommand("current-project");

  // Animation frame for syncing video time with store
  useEffect(() => {
    let animationFrameId: number;
    
    const updateTime = () => {
      if (videoRef.current) {
        setCurrentTime(videoRef.current.currentTime);
      }
      animationFrameId = requestAnimationFrame(updateTime);
    };
    
    animationFrameId = requestAnimationFrame(updateTime);
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [setCurrentTime]);

  const handleVideoSelect = (video: any) => {
    setClips([]);
    setActiveVideoAsset(video);
    
    if (video.src) {
      setVideoSrc(video.src);
    }
    
    toast({
      title: "Video selected",
      description: `${video.name} is now ready to edit`,
    });
  };

  const handleVideoDrop = (file: File, track: number, dropTime: number) => {
    const videoUrl = URL.createObjectURL(file);
    
    const video = document.createElement("video");
    video.src = videoUrl;
    
    video.onloadedmetadata = () => {
      const clipDuration = video.duration;
      const newClip: Clip = {
        id: `clip-${Date.now()}`,
        start: dropTime,
        end: dropTime + clipDuration,
        track,
        type: "video",
        name: file.name
      };
      
      setClips([...clips, newClip]);
      setSelectedClipId(newClip.id);
      
      if (!videoSrc) {
        setVideoSrc(videoUrl);
        setDuration(clipDuration);
      }
      
      toast({
        title: "Video added to timeline",
        description: `${file.name} has been added to track ${track + 1}`,
      });
    };
  };

  const handleVideoAssetDrop = (videoAsset: any, track: number, dropTime: number) => {
    // Set video source if needed
    const videoSrc = videoAsset.src;
    if (!videoSrc) {
      toast({
        title: "Error",
        description: "Video source not found",
        variant: "destructive"
      });
      return;
    }

    // Create a video element to get the duration
    const video = document.createElement("video");
    video.src = videoSrc;
    
    video.onloadedmetadata = () => {
      // Create a new clip for the timeline
      const clipDuration = videoAsset.duration || video.duration;
      const newClip: Clip = {
        id: `clip-${Date.now()}`,
        start: dropTime,
        end: dropTime + clipDuration,
        track,
        type: "video",
        name: videoAsset.name
      };
      
      setClips([...clips, newClip]);
      setSelectedClipId(newClip.id);
      
      toast({
        title: "Video added to timeline",
        description: `${videoAsset.name} has been added to track ${track + 1}`,
      });
    };
    
    video.onerror = () => {
      toast({
        title: "Error",
        description: "Failed to load video for timeline",
        variant: "destructive"
      });
    };
  };

  const handleChatCommand = async (command: string) => {
    if (!selectedClipId && clips.length === 0) {
      toast({
        title: "No video available",
        description: "Please add a video to the timeline first",
        variant: "destructive",
      });
      return;
    }
    
    console.log("Processing command:", command);
    
    // Use our command hook to process the NLP request
    const result = await executeCommand(command);
    
    if (result && result.operations.length > 0) {
      // Apply the operations to the timeline
      applyOperationsToTimeline(result.operations);
    }
  };

  // Apply AI operations to the timeline
  const applyOperationsToTimeline = (operations: Operation[]) => {
    // Convert operations to clips
    const newClips = operations.map(op => {
      const clipId = `clip-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      
      return {
        id: clipId,
        start: op.start_sec,
        end: op.end_sec,
        track: determineTrackForEffect(op.effect),
        type: op.effect,
        name: `${op.effect.charAt(0).toUpperCase() + op.effect.slice(1)} Effect`
      };
    });
    
    setClips([...clips, ...newClips]);
    
    if (newClips.length > 0) {
      setSelectedClipId(newClips[0].id);
      
      toast({
        title: "Edits applied",
        description: `${newClips.length} operations added to timeline`,
      });
    }
  };
  
  const determineTrackForEffect = (effect: string): number => {
    switch (effect) {
      case "cut":
      case "speed":
        return 0; // Video track
      case "textOverlay":
      case "caption":
        return 1; // Text track
      case "fade":
        return 3; // Effects track
      case "colorGrade":
      case "brightness":
        return 4; // Format track
      default:
        return 2; // Other track
    }
  };

  const handleSaveProject = () => {
    toast({
      title: "Project saved",
      description: "Your project has been saved successfully",
    });
  };

  const handleRenderVideo = () => {
    toast({
      title: "Rendering started",
      description: "Your video is now being rendered",
    });
  };

  // Handlers for layout changes
  const handleSidebarResize = (sizes: number[]) => {
    setLayoutSize('sidebar', sizes[0]);
  };

  const handleMainPaneResize = (sizes: number[]) => {
    setLayoutSize('preview', sizes[0]);
    setLayoutSize('chat', sizes[1]);
  };

  const handleTimelineResize = (sizes: number[]) => {
    setLayoutSize('timeline', sizes[1]);
  };

  return (
    <div className="flex flex-col h-screen bg-cre8r-dark text-white">
      <NavBar />
      
      <div className="flex justify-between items-center px-4 h-14 border-b border-cre8r-gray-700 bg-cre8r-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-cre8r-violet rounded-full flex items-center justify-center">
            <Film className="h-5 w-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold">
            {activeVideoAsset ? `Editing: ${activeVideoAsset.name}` : "Untitled Project"}
          </h1>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            className="border-cre8r-gray-600 hover:border-cre8r-violet"
            onClick={() => undo()}
            disabled={history.past.length === 0}
          >
            <UndoIcon className="h-4 w-4" />
          </Button>
          
          <Button
            variant="outline"
            className="border-cre8r-gray-600 hover:border-cre8r-violet"
            onClick={() => redo()}
            disabled={history.future.length === 0}
          >
            <RedoIcon className="h-4 w-4" />
          </Button>
          
          <Button
            variant="outline"
            className="border-cre8r-gray-600 hover:border-cre8r-violet"
            onClick={handleSaveProject}
          >
            <Save className="h-4 w-4 mr-2" />
            Save Project
          </Button>
          
          <Button
            className="bg-cre8r-violet hover:bg-cre8r-violet-dark"
            onClick={handleRenderVideo}
          >
            Render Video
          </Button>
        </div>
      </div>
      
      {/* Main resizable layout */}
      <div className="flex-1 overflow-hidden">
        <ResizablePanelGroup
          direction="horizontal" 
          onLayout={handleSidebarResize}
        >
          {/* Left sidebar with assets */}
          <ResizablePanel 
            defaultSize={layout.sidebar} 
            minSize={15}
            className="flex"
          >
            <AssetsIconBar />
          </ResizablePanel>
          
          {/* Divider between sidebar and main content */}
          <ResizableHandle withHandle className="bg-cre8r-gray-700 hover:bg-cre8r-violet transition-colors" />
          
          {/* Main content area with nested panel groups */}
          <ResizablePanel>
            <ResizablePanelGroup 
              direction="vertical"
              onLayout={handleTimelineResize}
            >
              {/* Top section with preview and chat */}
              <ResizablePanel>
                <ResizablePanelGroup 
                  direction="horizontal"
                  onLayout={handleMainPaneResize}
                >
                  {/* Video preview */}
                  <ResizablePanel 
                    defaultSize={layout.preview} 
                    minSize={50}
                    className="flex-1 min-h-0"
                  >
                    <VideoPlayer
                      ref={videoRef}
                      src={videoSrc}
                      currentTime={currentTime}
                      onTimeUpdate={setCurrentTime}
                      onDurationChange={setDuration}
                      className="h-full"
                      rightControl={<TimecodeDisplay />}
                    />
                  </ResizablePanel>
                  
                  {/* Divider between preview and chat */}
                  <ResizableHandle withHandle className="bg-cre8r-gray-700 hover:bg-cre8r-violet transition-colors" />
                  
                  {/* Chat panel */}
                  <ResizablePanel 
                    defaultSize={layout.chat} 
                    minSize={20}
                    className="w-1/5 min-w-[280px]"
                  >
                    <ChatPanel onChatCommand={handleChatCommand} />
                  </ResizablePanel>
                </ResizablePanelGroup>
              </ResizablePanel>
              
              {/* Divider between top section and timeline */}
              <ResizableHandle withHandle className="bg-cre8r-gray-700 hover:bg-cre8r-violet transition-colors" />
              
              {/* Timeline section */}
              <ResizablePanel 
                defaultSize={layout.timeline} 
                minSize={15}
              >
                <Timeline
                  ref={timelineRef}
                  duration={duration}
                  currentTime={currentTime}
                  onTimeUpdate={setCurrentTime}
                  clips={clips}
                  onClipSelect={setSelectedClipId}
                  selectedClipId={selectedClipId}
                  onVideoDrop={handleVideoDrop}
                  onVideoAssetDrop={handleVideoAssetDrop}
                />
              </ResizablePanel>
            </ResizablePanelGroup>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
};

export default Editor;
