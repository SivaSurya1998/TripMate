import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Calendar, Clock, MapPin, Plus, Mail, Download, Plane, Hotel, UtensilsCrossed, Camera, Loader2 } from 'lucide-react';
import { itineraryAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const Itinerary = () => {
  const [events, setEvents] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const { toast } = useToast();
  const [newEvent, setNewEvent] = useState({
    title: '',
    date: '',
    time: '',
    location: '',
    description: '',
    type: 'activity'
  });

  const eventTypeIcons = {
    flight: <Plane className="h-4 w-4" />,
    accommodation: <Hotel className="h-4 w-4" />,
    dining: <UtensilsCrossed className="h-4 w-4" />,
    activity: <Camera className="h-4 w-4" />
  };

  const eventTypeColors = {
    flight: 'bg-blue-100 text-blue-800 border-blue-200',
    accommodation: 'bg-purple-100 text-purple-800 border-purple-200',
    dining: 'bg-orange-100 text-orange-800 border-orange-200',
    activity: 'bg-green-100 text-green-800 border-green-200'
  };

  // Load events on component mount
  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const eventsData = await itineraryAPI.getEvents();
      setEvents(eventsData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load events. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const addEvent = async () => {
    if (!newEvent.title || !newEvent.date || !newEvent.time) {
      toast({
        title: "Missing Information",
        description: "Please fill in title, date, and time.",
        variant: "destructive",
      });
      return;
    }

    try {
      setAdding(true);
      const createdEvent = await itineraryAPI.createEvent(newEvent);
      setEvents(prev => [...prev, createdEvent].sort((a, b) => 
        new Date(`${a.date} ${a.time}`) - new Date(`${b.date} ${b.time}`)
      ));
      setNewEvent({
        title: '',
        date: '',
        time: '',
        location: '',
        description: '',
        type: 'activity'
      });
      setShowAddForm(false);
      toast({
        title: "Event Added",
        description: `${createdEvent.title} has been added to your itinerary`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add event. Please try again.",
        variant: "destructive",
      });
    } finally {
      setAdding(false);
    }
  };

  const deleteEvent = async (eventId) => {
    try {
      await itineraryAPI.deleteEvent(eventId);
      setEvents(prev => prev.filter(event => event.id !== eventId));
      toast({
        title: "Event Deleted",
        description: "Event has been removed from your itinerary",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete event. Please try again.",
        variant: "destructive",
      });
    }
  };

  const exportItinerary = () => {
    const content = events.map(event => 
      `${event.title}\n${event.date} at ${event.time}\n${event.location}\n${event.description}\n---\n`
    ).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'trip-itinerary.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const emailItinerary = () => {
    const subject = encodeURIComponent('My Trip Itinerary');
    const body = encodeURIComponent(
      events.map(event => 
        `${event.title}\n${event.date} at ${event.time}\n${event.location}\n${event.description}\n\n`
      ).join('')
    );
    window.open(`mailto:?subject=${subject}&body=${body}`);
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const groupEventsByDate = (events) => {
    return events.reduce((groups, event) => {
      const date = event.date;
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(event);
      return groups;
    }, {});
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading events...</span>
      </div>
    );
  }

  const groupedEvents = groupEventsByDate(events);

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <Card className="bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-indigo-900 mb-2">Trip Itinerary</h2>
              <p className="text-indigo-600">{events.length} events planned</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={emailItinerary} className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Email
              </Button>
              <Button variant="outline" onClick={exportItinerary} className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Export
              </Button>
              <Button onClick={() => setShowAddForm(!showAddForm)} className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Add Event
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Add Event Form */}
      {showAddForm && (
        <Card className="border-2 border-dashed border-primary/30">
          <CardHeader>
            <CardTitle>Add New Event</CardTitle>
            <CardDescription>Fill in the details for your trip event</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                placeholder="Event title"
                value={newEvent.title}
                onChange={(e) => setNewEvent(prev => ({ ...prev, title: e.target.value }))}
              />
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                value={newEvent.type}
                onChange={(e) => setNewEvent(prev => ({ ...prev, type: e.target.value }))}
              >
                <option value="activity">Activity</option>
                <option value="flight">Flight</option>
                <option value="accommodation">Accommodation</option>
                <option value="dining">Dining</option>
              </select>
              <Input
                type="date"
                value={newEvent.date}
                onChange={(e) => setNewEvent(prev => ({ ...prev, date: e.target.value }))}
              />
              <Input
                type="time"
                value={newEvent.time}
                onChange={(e) => setNewEvent(prev => ({ ...prev, time: e.target.value }))}
              />
              <Input
                placeholder="Location"
                value={newEvent.location}
                onChange={(e) => setNewEvent(prev => ({ ...prev, location: e.target.value }))}
                className="md:col-span-2"
              />
              <Textarea
                placeholder="Description"
                value={newEvent.description}
                onChange={(e) => setNewEvent(prev => ({ ...prev, description: e.target.value }))}
                className="md:col-span-2"
              />
            </div>
            <div className="flex gap-2 mt-4">
              <Button onClick={addEvent} disabled={adding}>
                {adding ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Add Event
              </Button>
              <Button variant="outline" onClick={() => setShowAddForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Events Timeline */}
      <div className="space-y-6">
        {Object.entries(groupedEvents).map(([date, dayEvents]) => (
          <div key={date} className="space-y-4">
            <div className="flex items-center gap-3 mb-4">
              <Calendar className="h-5 w-5 text-primary" />
              <h3 className="text-xl font-bold text-primary">{formatDate(date)}</h3>
              <div className="flex-1 h-px bg-border"></div>
            </div>
            
            <div className="space-y-3 pl-8">
              {dayEvents.map((event, index) => (
                <Card key={event.id} className="hover:shadow-md transition-all duration-200">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className={`p-2 rounded-full ${eventTypeColors[event.type]} border`}>
                        {eventTypeIcons[event.type]}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold text-lg mb-1">{event.title}</h4>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                              <div className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {event.time}
                              </div>
                              <div className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" />
                                {event.location}
                              </div>
                            </div>
                            <p className="text-sm text-muted-foreground">{event.description}</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className={eventTypeColors[event.type]}>
                              {event.type}
                            </Badge>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => deleteEvent(event.id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              Delete
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
        
        {events.length === 0 && (
          <div className="text-center py-8">
            <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">No events scheduled yet. Add your first event to get started!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Itinerary;