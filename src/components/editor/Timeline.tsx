
import { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

interface TimelineProps {
  duration: number; // in seconds
  currentTime: number; // in seconds
  onTimeUpdate: (time: number) => void;
  clips?: {
    id: string;
    start: number;
    end: number;
    track: number;
  }[];
}

const Timeline = ({
  duration,
  currentTime,
  onTimeUpdate,
  clips = [],
}: TimelineProps) => {
  const timelineRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [zoom, setZoom] = useState(1);
  const trackCount = 6;

  // Format time as mm:ss
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Generate time markers based on duration and zoom
  const generateTimeMarkers = () => {
    const markers = [];
    const step = 5; // 5 second intervals
    for (let i = 0; i <= duration; i += step) {
      markers.push(
        <div
          key={i}
          className="absolute h-3 border-l border-cre8r-gray-600 text-xs text-cre8r-gray-400"
          style={{ left: `${(i / duration) * 100}%` }}
        >
          <span className="absolute top-3 left-1">{formatTime(i)}</span>
        </div>
      );
    }
    return markers;
  };

  // Handle playhead position when timeline is clicked
  const handleTimelineClick = (e: React.MouseEvent) => {
    if (!timelineRef.current) return;

    const rect = timelineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const clickedTime = (x / rect.width) * duration;
    onTimeUpdate(Math.max(0, Math.min(duration, clickedTime)));
  };

  // Handle mouse down on playhead
  const handlePlayheadMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsDragging(true);
  };

  // Handle mouse move when dragging playhead
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !timelineRef.current) return;

      const rect = timelineRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const newTime = (x / rect.width) * duration;
      onTimeUpdate(Math.max(0, Math.min(duration, newTime)));
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener("mousemove", handleMouseMove);
      document.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, duration, onTimeUpdate]);

  return (
    <div className="h-full flex flex-col bg-cre8r-gray-900 border-t border-cre8r-gray-700 select-none">
      <div className="flex items-center justify-between p-2 bg-cre8r-gray-800 border-b border-cre8r-gray-700">
        <div className="flex items-center gap-2">
          <button 
            className="p-1 hover:bg-cre8r-gray-700 rounded" 
            onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-minus"><path d="M5 12h14"/></svg>
          </button>
          <span className="text-xs text-cre8r-gray-300">{Math.round(zoom * 100)}%</span>
          <button 
            className="p-1 hover:bg-cre8r-gray-700 rounded" 
            onClick={() => setZoom(Math.min(2, zoom + 0.1))}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-plus"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          </button>
        </div>
        <div className="text-sm text-cre8r-gray-200">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      <div className="relative flex-1 overflow-x-auto overflow-y-hidden p-2 bg-cre8r-gray-900">
        {/* Timeline with markers */}
        <div 
          ref={timelineRef}
          className="relative h-full"
          style={{ width: `${100 * zoom}%`, minWidth: "100%" }}
          onClick={handleTimelineClick}
        >
          {/* Time markers */}
          <div className="h-6 border-b border-cre8r-gray-700 relative mb-1">
            {generateTimeMarkers()}
          </div>

          {/* Tracks */}
          <div className="flex flex-col gap-1">
            {Array.from({ length: trackCount }).map((_, index) => (
              <div 
                key={index} 
                className="h-12 bg-cre8r-gray-800 rounded border border-cre8r-gray-700 relative"
              >
                {/* Render clips for this track */}
                {clips.filter(clip => clip.track === index).map((clip) => (
                  <div
                    key={clip.id}
                    className="video-timeline-marker absolute h-10 my-1 rounded opacity-80 overflow-hidden"
                    style={{
                      left: `${(clip.start / duration) * 100}%`,
                      width: `${((clip.end - clip.start) / duration) * 100}%`,
                    }}
                  >
                    <div className="h-full w-full bg-gradient-to-r from-cre8r-violet-dark to-cre8r-violet flex items-center justify-center">
                      <span className="text-xs text-white truncate px-1">
                        {formatTime(clip.end - clip.start)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>

          {/* Playhead */}
          <div 
            className={cn(
              "absolute top-0 bottom-0 w-0.5 bg-red-500 z-10 cursor-ew-resize",
              isDragging && "bg-red-400"
            )}
            style={{ left: `${(currentTime / duration) * 100}%` }}
            onMouseDown={handlePlayheadMouseDown}
          >
            <div className="w-3 h-3 bg-red-500 rounded-full -ml-1.5 -mt-1.5 absolute top-6"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Timeline;
