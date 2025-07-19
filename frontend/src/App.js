import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Card, CardContent } from "./components/ui/card";
import { Package, Calendar, DollarSign, Plane } from "lucide-react";
import { Toaster } from "./components/ui/toaster";
import PackingList from "./components/PackingList";
import Itinerary from "./components/Itinerary";
import CurrencyConverter from "./components/CurrencyConverter";

const Home = () => {
  const [activeTab, setActiveTab] = useState("packing");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-xl">
              <Plane className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                TripMate
              </h1>
              <p className="text-sm text-muted-foreground">Your All-in-One Travel Companion</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Card className="bg-white/90 backdrop-blur-sm shadow-xl border-0">
          <CardContent className="p-0">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3 bg-muted/50 p-1 h-auto">
                <TabsTrigger 
                  value="packing" 
                  className="flex items-center gap-2 py-3 data-[state=active]:bg-white data-[state=active]:shadow-sm"
                >
                  <Package className="h-4 w-4" />
                  <span className="hidden sm:inline">Packing List</span>
                  <span className="sm:hidden">Pack</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="itinerary" 
                  className="flex items-center gap-2 py-3 data-[state=active]:bg-white data-[state=active]:shadow-sm"
                >
                  <Calendar className="h-4 w-4" />
                  <span className="hidden sm:inline">Itinerary</span>
                  <span className="sm:hidden">Plan</span>
                </TabsTrigger>
                <TabsTrigger 
                  value="converter" 
                  className="flex items-center gap-2 py-3 data-[state=active]:bg-white data-[state=active]:shadow-sm"
                >
                  <DollarSign className="h-4 w-4" />
                  <span className="hidden sm:inline">Converter</span>
                  <span className="sm:hidden">Convert</span>
                </TabsTrigger>
              </TabsList>

              <div className="p-6">
                <TabsContent value="packing" className="mt-0">
                  <PackingList />
                </TabsContent>
                <TabsContent value="itinerary" className="mt-0">
                  <Itinerary />
                </TabsContent>
                <TabsContent value="converter" className="mt-0">
                  <CurrencyConverter />
                </TabsContent>
              </div>
            </Tabs>
          </CardContent>
        </Card>
      </main>

      {/* Footer */}
      <footer className="bg-white/80 backdrop-blur-md border-t mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-sm text-muted-foreground">
            <p>Built with ❤️ for travelers worldwide</p>
            <p className="mt-1 text-xs">
              ✨ Powered by React + FastAPI + MongoDB - Ready for Deployment!
            </p>
          </div>
        </div>
      </footer>

      {/* Toast Notifications */}
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;