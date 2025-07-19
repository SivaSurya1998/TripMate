import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { ArrowUpDown, DollarSign, TrendingUp, Settings } from 'lucide-react';
import { exchangeRates, currencies } from '../data/mockData';

const CurrencyConverter = () => {
  const [amount, setAmount] = useState('100');
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('EUR');
  const [convertedAmount, setConvertedAmount] = useState('');
  const [showRateSettings, setShowRateSettings] = useState(false);
  const [customRates, setCustomRates] = useState(exchangeRates);

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const updateRate = (pair, newRate) => {
    setCustomRates(prev => ({
      ...prev,
      [pair]: { ...prev[pair], rate: parseFloat(newRate) }
    }));
  };

  useEffect(() => {
    if (amount && fromCurrency && toCurrency) {
      const rateKey = `${fromCurrency}_${toCurrency}`;
      const rate = customRates[rateKey]?.rate;
      
      if (rate) {
        const result = (parseFloat(amount) * rate).toFixed(2);
        setConvertedAmount(result);
      } else {
        // Calculate inverse rate if direct rate doesn't exist
        const inverseKey = `${toCurrency}_${fromCurrency}`;
        const inverseRate = customRates[inverseKey]?.rate;
        if (inverseRate) {
          const result = (parseFloat(amount) / inverseRate).toFixed(2);
          setConvertedAmount(result);
        } else {
          setConvertedAmount('Rate not available');
        }
      }
    }
  }, [amount, fromCurrency, toCurrency, customRates]);

  const getCurrentRate = () => {
    const rateKey = `${fromCurrency}_${toCurrency}`;
    const rate = customRates[rateKey]?.rate;
    if (rate) return rate;
    
    const inverseKey = `${toCurrency}_${fromCurrency}`;
    const inverseRate = customRates[inverseKey]?.rate;
    if (inverseRate) return (1 / inverseRate).toFixed(4);
    
    return 'N/A';
  };

  const getCurrencySymbol = (code) => {
    return currencies.find(c => c.code === code)?.symbol || code;
  };

  const quickAmounts = ['10', '50', '100', '500', '1000'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-r from-emerald-50 to-teal-50 border-emerald-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-emerald-900 mb-2">Currency Converter</h2>
              <p className="text-emerald-600">Quick and easy currency conversions</p>
            </div>
            <Button 
              variant="outline" 
              onClick={() => setShowRateSettings(!showRateSettings)}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Manage Rates
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Rate Settings */}
      {showRateSettings && (
        <Card className="border-2 border-dashed border-primary/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Exchange Rate Settings
            </CardTitle>
            <CardDescription>Customize your exchange rates for accurate conversions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(customRates).map(([pair, data]) => (
                <div key={pair} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{pair.replace('_', ' → ')}</span>
                    <Badge variant="outline" className="text-xs">
                      Updated {data.lastUpdated}
                    </Badge>
                  </div>
                  <Input
                    type="number"
                    step="0.0001"
                    value={data.rate}
                    onChange={(e) => updateRate(pair, e.target.value)}
                    className="text-sm"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Converter */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-6">
            {/* Quick Amount Buttons */}
            <div>
              <label className="text-sm font-medium mb-2 block">Quick amounts:</label>
              <div className="flex gap-2 flex-wrap">
                {quickAmounts.map((quickAmount) => (
                  <Button
                    key={quickAmount}
                    variant={amount === quickAmount ? "default" : "outline"}
                    size="sm"
                    onClick={() => setAmount(quickAmount)}
                  >
                    {getCurrencySymbol(fromCurrency)}{quickAmount}
                  </Button>
                ))}
              </div>
            </div>

            {/* From Currency */}
            <div className="space-y-2">
              <label className="text-sm font-medium">From</label>
              <div className="flex gap-2">
                <select
                  className="flex h-10 w-32 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={fromCurrency}
                  onChange={(e) => setFromCurrency(e.target.value)}
                >
                  {currencies.map((currency) => (
                    <option key={currency.code} value={currency.code}>
                      {currency.code}
                    </option>
                  ))}
                </select>
                <Input
                  type="number"
                  placeholder="Enter amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="flex-1 text-lg font-medium"
                />
              </div>
            </div>

            {/* Swap Button */}
            <div className="flex justify-center">
              <Button
                variant="outline"
                size="sm"
                onClick={swapCurrencies}
                className="hover:scale-110 transition-transform duration-200"
              >
                <ArrowUpDown className="h-4 w-4" />
              </Button>
            </div>

            {/* To Currency */}
            <div className="space-y-2">
              <label className="text-sm font-medium">To</label>
              <div className="flex gap-2">
                <select
                  className="flex h-10 w-32 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                  value={toCurrency}
                  onChange={(e) => setToCurrency(e.target.value)}
                >
                  {currencies.map((currency) => (
                    <option key={currency.code} value={currency.code}>
                      {currency.code}
                    </option>
                  ))}
                </select>
                <div className="flex-1 relative">
                  <Input
                    value={convertedAmount}
                    readOnly
                    className="text-lg font-bold text-primary bg-primary/5"
                  />
                  <DollarSign className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-primary" />
                </div>
              </div>
            </div>

            {/* Rate Information */}
            <Card className="bg-muted/30">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Exchange Rate</span>
                  <span className="font-medium">
                    1 {fromCurrency} = {getCurrentRate()} {toCurrency}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Conversion Result */}
            {amount && convertedAmount && convertedAmount !== 'Rate not available' && (
              <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
                <CardContent className="p-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-800 mb-1">
                      {getCurrencySymbol(fromCurrency)}{amount} = {getCurrencySymbol(toCurrency)}{convertedAmount}
                    </div>
                    <div className="text-sm text-green-600">
                      Converted at rate: 1 {fromCurrency} = {getCurrentRate()} {toCurrency}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CurrencyConverter;