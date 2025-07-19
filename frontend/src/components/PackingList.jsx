import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Checkbox } from './ui/checkbox';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Plus, Package, CheckCircle2 } from 'lucide-react';
import { tripTypes } from '../data/mockData';

const PackingList = () => {
  const [selectedTrip, setSelectedTrip] = useState(tripTypes[0]);
  const [items, setItems] = useState(selectedTrip.items);
  const [newItem, setNewItem] = useState('');

  const handleTripChange = (trip) => {
    setSelectedTrip(trip);
    setItems(trip.items);
  };

  const toggleItem = (itemId) => {
    setItems(prev => prev.map(item => 
      item.id === itemId ? { ...item, packed: !item.packed } : item
    ));
  };

  const addItem = () => {
    if (newItem.trim()) {
      const item = {
        id: Date.now(),
        name: newItem.trim(),
        category: 'custom',
        packed: false
      };
      setItems(prev => [...prev, item]);
      setNewItem('');
    }
  };

  const packedCount = items.filter(item => item.packed).length;
  const totalCount = items.length;
  const progress = totalCount > 0 ? (packedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Trip Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tripTypes.map((trip) => (
          <Card 
            key={trip.id} 
            className={`cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-lg ${
              selectedTrip.id === trip.id ? 'ring-2 ring-primary shadow-lg' : ''
            }`}
            onClick={() => handleTripChange(trip)}
          >
            <CardContent className={`p-6 bg-gradient-to-br ${trip.color} text-white rounded-lg`}>
              <div className="text-center">
                <div className="text-4xl mb-2">{trip.icon}</div>
                <h3 className="font-bold text-lg">{trip.name}</h3>
                <p className="text-sm opacity-90">{trip.items.length} essential items</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Progress Section */}
      <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Package className="h-6 w-6 text-green-600" />
              <div>
                <h3 className="font-bold text-green-800">Packing Progress</h3>
                <p className="text-sm text-green-600">{selectedTrip.name}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-800">{Math.round(progress)}%</div>
              <div className="text-sm text-green-600">{packedCount} of {totalCount} packed</div>
            </div>
          </div>
          <div className="w-full bg-green-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </CardContent>
      </Card>

      {/* Add New Item */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add Custom Item
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Enter item name..."
              value={newItem}
              onChange={(e) => setNewItem(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addItem()}
              className="flex-1"
            />
            <Button onClick={addItem} disabled={!newItem.trim()}>
              Add Item
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Items List */}
      <Card>
        <CardHeader>
          <CardTitle>Packing Checklist</CardTitle>
          <CardDescription>Check off items as you pack them</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {items.map((item) => (
              <div 
                key={item.id}
                className={`flex items-center justify-between p-3 rounded-lg transition-all duration-200 hover:bg-muted/50 ${
                  item.packed ? 'bg-green-50 border border-green-200' : 'bg-white border border-border'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={item.packed}
                    onCheckedChange={() => toggleItem(item.id)}
                    className="h-5 w-5"
                  />
                  <span className={`font-medium ${item.packed ? 'line-through text-muted-foreground' : ''}`}>
                    {item.name}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {item.packed && <CheckCircle2 className="h-4 w-4 text-green-600" />}
                  <Badge variant={item.category === 'custom' ? 'secondary' : 'outline'}>
                    {item.category}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PackingList;