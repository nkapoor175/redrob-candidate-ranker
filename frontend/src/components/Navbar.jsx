import React, { useState, useEffect, useRef } from 'react';
import { Bell, ChevronDown, CheckCircle2, AlertCircle, Info } from 'lucide-react';

export default function Navbar() {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "Model Execution Success",
      message: "Candidate matching scores and rankings generated successfully.",
      time: "2 mins ago",
      type: "success",
      read: false
    },
    {
      id: 2,
      title: "New Candidate Uploaded",
      message: "Rahul Sharma's updated profile dataset parsed without errors.",
      time: "1 hour ago",
      type: "info",
      read: false
    },
    {
      id: 3,
      title: "System Warning",
      message: "Vite dev server initialized using standard execution policy bypass.",
      time: "2 hours ago",
      type: "warning",
      read: true
    }
  ]);

  const dropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-amber-400" />;
      default:
        return <Info className="h-4 w-4 text-sky-400" />;
    }
  };

  return (
    <header className="h-16 bg-[#1E293B]/60 backdrop-blur-md border-b border-slate-800 px-8 flex items-center justify-between sticky top-0 z-40">
      {/* Breadcrumb/Title */}
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold px-2 py-0.5 bg-sky-500/10 border border-sky-400/20 text-sky-400 rounded">
          Hackathon v1.0
        </span>
        <h1 className="text-sm font-semibold text-slate-300">
          AI-Powered Candidate Ranking System
        </h1>
      </div>

      {/* Action Items */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-full transition-all duration-200 relative"
          >
            <Bell className="h-5 w-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-sky-400 animate-pulse glow-cyan" />
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-[#1E293B] border border-slate-700/80 rounded-xl shadow-xl z-50 overflow-hidden">
              <div className="px-4 py-3 bg-slate-800/80 border-b border-slate-700/80 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-200">Notifications</span>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-[10px] text-sky-400 hover:text-sky-300 font-medium"
                  >
                    Mark all read
                  </button>
                )}
              </div>
              <div className="divide-y divide-slate-800 max-h-64 overflow-y-auto">
                {notifications.map((notif) => (
                  <div
                    key={notif.id}
                    className={`p-4 transition-colors duration-200 hover:bg-slate-800/40 ${
                      !notif.read ? 'bg-sky-500/[0.02]' : ''
                    }`}
                  >
                    <div className="flex gap-2.5 items-start">
                      <div className="mt-0.5 shrink-0">{getIcon(notif.type)}</div>
                      <div className="flex-1">
                        <div className="flex justify-between items-baseline mb-0.5">
                          <p className={`text-xs font-semibold ${!notif.read ? 'text-slate-200' : 'text-slate-400'}`}>
                            {notif.title}
                          </p>
                          <span className="text-[9px] text-slate-500 font-medium shrink-0">{notif.time}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{notif.message}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-slate-800" />

        {/* User Profile */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col text-right hidden sm:flex">
            <span className="text-xs font-semibold text-slate-200">Kaarthik Reddy</span>
            <span className="text-[10px] text-slate-500">Lead Recruiter</span>
          </div>
          <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-sky-400 to-blue-500 p-[1.5px] cursor-pointer shadow-lg shadow-sky-500/10">
            <div className="h-full w-full rounded-full bg-slate-800 overflow-hidden flex items-center justify-center">
              {/* Generated user avatar initials or placeholder */}
              <span className="text-xs font-bold text-sky-400">KR</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
