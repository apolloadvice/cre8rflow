
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import NavBar from "@/components/NavBar";
import AssetPanel from "@/components/editor/AssetPanel";
import VideoPlayer from "@/components/editor/VideoPlayer";
import Timeline from "@/components/editor/Timeline";
import ChatPanel from "@/components/editor/ChatPanel";
import { Button } from "@/components/ui/button";
import { Save, Film } from "lucide-react";
import { useThumbnails } from "@/hooks/useThumbnails";
import { useCommand, Operation } from "@/hooks/useCommand";

const SAMPLE_VIDEO_URL = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4";

interface Clip {
  id: string;
  start: number;
  end: number;
  track: number;
  type: string;
  name: string;
}

interface VideoAsset {
  id: string;
  name: string;
  thumbnail: string;
  duration: number;
  uploaded: Date;
  src?: string;
}

const Editor = () => {
  const { toast } = useToast();
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [videoSrc, setVideoSrc] = useState<string | undefined>(undefined);
  const [clips, setClips] = useState<Clip[]>([]);
  const [activeVideoAsset, setActiveVideoAsset] = useState<VideoAsset | null>(null);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
  
  // Integrate our new hooks
  const { thumbnailData } = useThumbnails(activeVideoAsset?.id);
  const { executeCommand } = useCommand("current-project");

  useEffect(() => {
    if (!activeVideoAsset) {
      const timer = setTimeout(() => {
        setVideoSrc(SAMPLE_VIDEO_URL);
        toast({
          title: "Video loaded",
          description: "Sample video loaded successfully",
        });
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [toast, activeVideoAsset]);

  // Effect to handle thumbnails when they're available
  useEffect(() => {
    if (thumbnailData) {
      console.log("Thumbnails loaded:", thumbnailData);
      // In a real implementation, this would update the UI to show thumbnails
    }
  }, [thumbnailData]);

  const handleVideoSelect = (video: VideoAsset) => {
    setClips([]);
    setActiveVideoAsset(video);
    
    if (video.src) {
      setVideoSrc(video.src);
    } else if (video.id === "1") {
      setVideoSrc(SAMPLE_VIDEO_URL);
    }
    
    toast({
      title: "Video selected",
      description: `${video.name} is now ready to edit`,
    });
    
    // In a real implementation, this would trigger a fetch for thumbnails
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
      
      setClips(prevClips => [...prevClips, newClip]);
      setSelectedClipId(newClip.id);
      
      if (!videoSrc) {
        setVideoSrc(videoUrl);
        setDuration(clipDuration);
      }
      
      toast({
        title: "Video added to timeline",
        description: `${file.name} has been added to track ${track + 1}`,
      });
      
      // In a real implementation, this would trigger thumbnail generation
      // simulateGenerateThumbnails(file);
    };
  };

  const handleVideoAssetDrop = (videoAsset: VideoAsset, track: number, dropTime: number) => {
    // Set video source if needed
    const videoSrc = videoAsset.src || (videoAsset.id === "1" ? SAMPLE_VIDEO_URL : undefined);
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
      
      setClips(prevClips => [...prevClips, newClip]);
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

  // New function to apply AI operations to the timeline
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
    
    setClips(prevClips => [...prevClips, ...newClips]);
    
    if (newClips.length > 0) {
      setSelectedClipId(newClips[0].id);
      
      toast({
        title: "Edits applied",
        description: `${newClips.length} operations added to timeline`,
      });
    }
  };
  
  // Helper function to determine which track to use based on effect type
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
      
      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/5 min-w-[240px] hidden md:block">
          <AssetPanel onVideoSelect={handleVideoSelect} />
        </div>
        
        <div className="flex-1 flex flex-col">
          <div className="flex-1 min-h-0">
            <VideoPlayer
              src={videoSrc}
              currentTime={currentTime}
              onTimeUpdate={setCurrentTime}
              onDurationChange={setDuration}
              className="h-full"
            />
          </div>
          <div className="h-64">
            <Timeline
              duration={duration}
              currentTime={currentTime}
              onTimeUpdate={setCurrentTime}
              clips={clips}
              onClipSelect={setSelectedClipId}
              selectedClipId={selectedClipId}
              onVideoDrop={handleVideoDrop}
              onVideoAssetDrop={handleVideoAssetDrop}
            />
          </div>
        </div>
        
        <div className="w-1/5 min-w-[280px] hidden md:block">
          <ChatPanel onChatCommand={handleChatCommand} />
        </div>
      </div>
    </div>
  );
};

export default Editor;
