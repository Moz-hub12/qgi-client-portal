import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// Optimized icon imports for tree-shaking
import Bell from 'lucide-react/dist/esm/icons/bell'
import Search from 'lucide-react/dist/esm/icons/search'
import Filter from 'lucide-react/dist/esm/icons/filter'
import AlertCircle from 'lucide-react/dist/esm/icons/alert-circle'
import Info from 'lucide-react/dist/esm/icons/info'
import CheckCircle from 'lucide-react/dist/esm/icons/check-circle'
import Clock from 'lucide-react/dist/esm/icons/clock'

const AnnouncementsPage = () => {
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [stats, setStats] = useState({
    total: 0,
    unread: 0,
    high_priority: 0,
    read: 0
  });

  // Demo data for announcements
  useEffect(() => {
    const demoAnnouncements = [
      {
        id: 1,
        title: 'Q3 2024 Performance Update',
        content: 'We are pleased to announce that your portfolio has achieved a 8.5% return for Q3 2024, outperforming the market benchmark by 2.3%. This strong performance is attributed to our strategic allocation in technology and healthcare sectors.',
        priority: 'high',
        category: 'performance',
        created_at: '2024-10-15T10:30:00Z',
        is_read: false
      },
      {
        id: 2,
        title: 'New Investment Opportunity Available',
        content: 'We have identified a new investment opportunity in renewable energy infrastructure. This opportunity aligns with our ESG investment strategy and offers potential returns of 12-15% annually. Please contact your advisor for more details.',
        priority: 'high',
        category: 'investment',
        created_at: '2024-10-12T14:20:00Z',
        is_read: false
      },
      {
        id: 3,
        title: 'Platform Maintenance Scheduled',
        content: 'We will be performing routine maintenance on our client portal on Sunday, October 20th from 2:00 AM to 6:00 AM EST. During this time, the portal may be temporarily unavailable. We apologize for any inconvenience.',
        priority: 'normal',
        category: 'technical',
        created_at: '2024-10-10T09:15:00Z',
        is_read: true
      },
      {
        id: 4,
        title: 'Monthly Statement Available',
        content: 'Your September 2024 monthly statement is now available in the Documents section. The statement includes detailed performance metrics, transaction history, and portfolio allocation updates.',
        priority: 'normal',
        category: 'documents',
        created_at: '2024-10-05T16:45:00Z',
        is_read: true
      },
      {
        id: 5,
        title: 'Holiday Schedule Notice',
        content: 'Please note that our offices will be closed on Monday, October 14th in observance of Columbus Day. Regular business hours will resume on Tuesday, October 15th. Emergency support remains available 24/7.',
        priority: 'low',
        category: 'general',
        created_at: '2024-10-01T11:00:00Z',
        is_read: true
      }
    ];

    // Simulate API loading
    setTimeout(() => {
      setAnnouncements(demoAnnouncements);
      setStats({
        total: demoAnnouncements.length,
        unread: demoAnnouncements.filter(a => !a.is_read).length,
        high_priority: demoAnnouncements.filter(a => a.priority === 'high').length,
        read: demoAnnouncements.filter(a => a.is_read).length
      });
      setLoading(false);
    }, 1000);
  }, []);

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'normal':
        return <Info className="h-4 w-4 text-blue-500" />;
      case 'low':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <Info className="h-4 w-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'normal':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredAnnouncements = announcements.filter(announcement => {
    const matchesSearch = announcement.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         announcement.content.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = priorityFilter === 'all' || announcement.priority === priorityFilter;
    return matchesSearch && matchesPriority;
  });

  const unreadAnnouncements = filteredAnnouncements.filter(a => !a.is_read);
  const readAnnouncements = filteredAnnouncements.filter(a => a.is_read);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
            <p className="text-gray-600 mt-2">Stay updated with the latest news and updates</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded mb-4"></div>
                <div className="h-8 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Announcements</h1>
          <p className="text-gray-600 mt-2">Stay updated with the latest news and updates</p>
        </div>
        <Bell className="h-8 w-8 text-gray-400" />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Bell className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Unread</p>
                <p className="text-2xl font-bold text-orange-600">{stats.unread}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-red-600">{stats.high_priority}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Read</p>
                <p className="text-2xl font-bold text-green-600">{stats.read}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search announcements..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Filter by priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="high">High Priority</SelectItem>
            <SelectItem value="normal">Normal Priority</SelectItem>
            <SelectItem value="low">Low Priority</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Announcements Tabs */}
      <Tabs defaultValue="all" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="all">All ({filteredAnnouncements.length})</TabsTrigger>
          <TabsTrigger value="unread">Unread ({unreadAnnouncements.length})</TabsTrigger>
          <TabsTrigger value="read">Read ({readAnnouncements.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {filteredAnnouncements.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No announcements found</h3>
                <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
              </CardContent>
            </Card>
          ) : (
            filteredAnnouncements.map((announcement) => (
              <Card key={announcement.id} className={`transition-all hover:shadow-md ${!announcement.is_read ? 'border-l-4 border-l-blue-500 bg-blue-50/30' : ''}`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getPriorityIcon(announcement.priority)}
                        <Badge variant="outline" className={getPriorityColor(announcement.priority)}>
                          {announcement.priority.charAt(0).toUpperCase() + announcement.priority.slice(1)}
                        </Badge>
                        <Badge variant="outline">
                          {announcement.category}
                        </Badge>
                        {!announcement.is_read && (
                          <Badge className="bg-blue-100 text-blue-800">New</Badge>
                        )}
                      </div>
                      <CardTitle className="text-xl">{announcement.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-2">
                        <Clock className="h-4 w-4" />
                        {formatDate(announcement.created_at)}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{announcement.content}</p>
                  {!announcement.is_read && (
                    <div className="mt-4 pt-4 border-t">
                      <Button variant="outline" size="sm">
                        Mark as Read
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="unread" className="space-y-4">
          {unreadAnnouncements.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
                <p className="text-gray-600">You have no unread announcements.</p>
              </CardContent>
            </Card>
          ) : (
            unreadAnnouncements.map((announcement) => (
              <Card key={announcement.id} className="border-l-4 border-l-blue-500 bg-blue-50/30 transition-all hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getPriorityIcon(announcement.priority)}
                        <Badge variant="outline" className={getPriorityColor(announcement.priority)}>
                          {announcement.priority.charAt(0).toUpperCase() + announcement.priority.slice(1)}
                        </Badge>
                        <Badge variant="outline">{announcement.category}</Badge>
                        <Badge className="bg-blue-100 text-blue-800">New</Badge>
                      </div>
                      <CardTitle className="text-xl">{announcement.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-2">
                        <Clock className="h-4 w-4" />
                        {formatDate(announcement.created_at)}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 leading-relaxed">{announcement.content}</p>
                  <div className="mt-4 pt-4 border-t">
                    <Button variant="outline" size="sm">
                      Mark as Read
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="read" className="space-y-4">
          {readAnnouncements.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No read announcements</h3>
                <p className="text-gray-600">Read announcements will appear here.</p>
              </CardContent>
            </Card>
          ) : (
            readAnnouncements.map((announcement) => (
              <Card key={announcement.id} className="transition-all hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        {getPriorityIcon(announcement.priority)}
                        <Badge variant="outline" className={getPriorityColor(announcement.priority)}>
                          {announcement.priority.charAt(0).toUpperCase() + announcement.priority.slice(1)}
                        </Badge>
                        <Badge variant="outline">{announcement.category}</Badge>
                      </div>
                      <CardTitle className="text-xl text-gray-700">{announcement.title}</CardTitle>
                      <CardDescription className="flex items-center gap-2 mt-2">
                        <Clock className="h-4 w-4" />
                        {formatDate(announcement.created_at)}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 leading-relaxed">{announcement.content}</p>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnnouncementsPage;

