
import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import NavBar from "@/components/NavBar";
import AssetPanel from "@/components/editor/AssetPanel";
import VideoPlayer from "@/components/editor/VideoPlayer";
import Timeline from "@/components/editor/Timeline";
import ChatPanel from "@/components/editor/ChatPanel";
import { Button } from "@/components/ui/button";
import { Save, Film } from "lucide-react";

// Sample video URL for demo purposes
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

  useEffect(() => {
    // Set the sample video after a short delay to simulate loading
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

  const handleVideoSelect = (video: VideoAsset) => {
    // Clear any existing clips when selecting a new video
    setClips([]);
    
    // Set the active video
    setActiveVideoAsset(video);
    
    // Update the video source for the player
    if (video.src) {
      setVideoSrc(video.src);
    } else if (video.id === "1") {
      // For the placeholder video
      setVideoSrc(SAMPLE_VIDEO_URL);
    }
    
    toast({
      title: "Video selected",
      description: `${video.name} is now ready to edit`,
    });
  };

  const handleChatCommand = (command: string) => {
    console.log("Processing command:", command);
    
    if (!videoSrc || duration === 0) {
      toast({
        title: "No video loaded",
        description: "Please upload or select a video first",
        variant: "destructive",
      });
      return;
    }
    
    // Process the command and create appropriate clips
    const lowerCommand = command.toLowerCase();
    
    // Simulate processing the command with loading state
    toast({
      title: "Processing command",
      description: "Analyzing your edit request...",
    });
    
    setTimeout(() => {
      const newClips: Clip[] = [];
      
      // Simple command parser
      if (lowerCommand.includes("trim") || lowerCommand.includes("cut")) {
        // Trim command creates a single clip
        const start = Math.max(0, currentTime);
        const end = Math.min(start + 10, duration);
        
        newClips.push({
          id: `trim-${Date.now()}`,
          start,
          end,
          track: 0,
          type: "trim",
          name: "Trim"
        });
      } 
      else if (lowerCommand.includes("highlight")) {
        // Highlight creates several clips
        for (let i = 0; i < 3; i++) {
          const start = Math.random() * (duration * 0.8);
          const clipDuration = Math.random() * 5 + 2; // 2-7 seconds
          const end = Math.min(start + clipDuration, duration);
          
          newClips.push({
            id: `highlight-${Date.now()}-${i}`,
            start,
            end,
            track: 0,
            type: "highlight",
            name: "Highlight"
          });
        }
      }
      else if (lowerCommand.includes("subtitle") || lowerCommand.includes("caption")) {
        // Subtitle adds a text track
        newClips.push({
          id: `subtitle-${Date.now()}`,
          start: 0,
          end: duration,
          track: 1, // Text track
          type: "subtitle",
          name: "Subtitles"
        });
      }
      else if (lowerCommand.includes("music") || lowerCommand.includes("audio")) {
        // Music adds an audio track
        newClips.push({
          id: `audio-${Date.now()}`,
          start: 0,
          end: duration,
          track: 2, // Audio track
          type: "audio",
          name: "Music"
        });
      }
      else if (lowerCommand.includes("silence") || lowerCommand.includes("quiet")) {
        // Auto-cut silence creates multiple short clips
        const silenceClips = [];
        let position = 0;
        
        while (position < duration) {
          const clipLength = Math.random() * 8 + 3; // 3-11 sec clips
          const gap = Math.random() * 1 + 0.2; // 0.2-1.2 sec gaps (silence)
          
          silenceClips.push({
            id: `silence-cut-${Date.now()}-${silenceClips.length}`,
            start: position,
            end: Math.min(position + clipLength, duration),
            track: 0,
            type: "cut",
            name: "Cut"
          });
          
          position += clipLength + gap;
        }
        
        newClips.push(...silenceClips);
      }
      else if (lowerCommand.includes("color") || lowerCommand.includes("grade")) {
        // Color grade effect on whole video
        newClips.push({
          id: `color-${Date.now()}`,
          start: 0,
          end: duration,
          track: 3, // Effects track
          type: "color",
          name: "Color Grade"
        });
      }
      else if (lowerCommand.includes("crop") || lowerCommand.includes("vertical")) {
        // Vertical crop effect
        newClips.push({
          id: `crop-${Date.now()}`,
          start: 0,
          end: duration,
          track: 4, // Format track
          type: "crop",
          name: "Vertical Crop"
        });
      }
      else {
        // Generic command - create 2-3 random clips
        const clipCount = Math.floor(Math.random() * 2) + 2;
        for (let i = 0; i < clipCount; i++) {
          const trackIndex = Math.floor(Math.random() * 3);
          const start = Math.random() * (duration * 0.8);
          const clipDuration = Math.random() * 10 + 5; // 5-15 seconds
          const end = Math.min(start + clipDuration, duration);
          
          newClips.push({
            id: `clip-${Date.now()}-${i}`,
            start,
            end,
            track: trackIndex,
            type: "generic",
            name: "Edit"
          });
        }
      }
      
      setClips((prevClips) => [...prevClips, ...newClips]);
      
      toast({
        title: "Edit applied",
        description: `Added ${newClips.length} new segments to the timeline`,
      });
      
    }, 1500);
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
        {/* Left panel - Asset browser */}
        <div className="w-1/5 min-w-[240px] hidden md:block">
          <AssetPanel onVideoSelect={handleVideoSelect} />
        </div>
        
        {/* Center panel - Video player and timeline */}
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
            />
          </div>
        </div>
        
        {/* Right panel - Chat interface */}
        <div className="w-1/5 min-w-[280px] hidden md:block">
          <ChatPanel onChatCommand={handleChatCommand} />
        </div>
      </div>
    </div>
  );
};

export default Editor;
