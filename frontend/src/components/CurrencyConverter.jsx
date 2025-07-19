import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { ArrowUpDown, DollarSign, TrendingUp, Settings, Loader2 } from 'lucide-react';
import { currencyAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const CurrencyConverter = () => {
  const [amount, setAmount] = useState('100');
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('EUR');
  const [convertedAmount, setConvertedAmount] = useState('');
  const [showRateSettings, setShowRateSettings] = useState(false);
  const [currencies, setCurrencies] = useState([]);
  const [exchangeRates, setExchangeRates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [converting, setConverting] = useState(false);
  const { toast } = useToast();

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Auto-convert when amount or currencies change
  useEffect(() => {
    if (amount && fromCurrency && toCurrency && currencies.length > 0) {
      handleConversion();
    }
  }, [amount, fromCurrency, toCurrency]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [currenciesData, ratesData] = await Promise.all([
        currencyAPI.getCurrencies(),
        currencyAPI.getExchangeRates()
      ]);
      setCurrencies(currenciesData);
      setExchangeRates(ratesData);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load currency data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleConversion = async () => {
    if (!amount || !fromCurrency || !toCurrency) return;

    try {
      setConverting(true);
      const result = await currencyAPI.convertCurrency(
        parseFloat(amount),
        fromCurrency,
        toCurrency
      );
      setConvertedAmount(result.converted_amount.toString());
    } catch (error) {
      setConvertedAmount('Rate not available');
      toast({
        title: "Conversion Error",
        description: "Exchange rate not found for this currency pair.",
        variant: "destructive",
      });
    } finally {
      setConverting(false);
    }
  };

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const updateRate = async (rateId, newRate) => {
    const rate = exchangeRates.find(r => r.id === rateId);
    if (!rate) return;

    try {
      await currencyAPI.updateExchangeRate(rate.from_currency, rate.to_currency, parseFloat(newRate));
      setExchangeRates(prev => prev.map(r => 
        r.id === rateId ? { ...r, rate: parseFloat(newRate) } : r
      ));
      toast({
        title: "Rate Updated",
        description: `Exchange rate for ${rate.from_currency}/${rate.to_currency} updated successfully`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update exchange rate.",
        variant: "destructive",
      });
    }
  };

  const getCurrentRate = () => {
    const rate = exchangeRates.find(r => 
      r.from_currency === fromCurrency && r.to_currency === toCurrency
    );
    if (rate) return rate.rate;
    
    const inverseRate = exchangeRates.find(r => 
      r.from_currency === toCurrency && r.to_currency === fromCurrency
    );
    if (inverseRate) return (1 / inverseRate.rate).toFixed(4);
    
    return 'N/A';
  };

  const getCurrencySymbol = (code) => {
    return currencies.find(c => c.code === code)?.symbol || code;
  };

  const quickAmounts = ['10', '50', '100', '500', '1000'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading currency data...</span>
      </div>
    );
  }

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
              {exchangeRates.map((rate) => (
                <div key={rate.id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{rate.from_currency} → {rate.to_currency}</span>
                    <Badge variant="outline" className="text-xs">
                      Updated {rate.last_updated}
                    </Badge>
                  </div>
                  <Input
                    type="number"
                    step="0.0001"
                    value={rate.rate}
                    onChange={(e) => updateRate(rate.id, e.target.value)}
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
                    value={converting ? 'Converting...' : convertedAmount}
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
            {amount && convertedAmount && convertedAmount !== 'Rate not available' && !converting && (
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