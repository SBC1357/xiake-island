/**
 * App Entry — 写作工作台路由系统
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { NewTaskPage } from './pages/NewTaskPage';
import { StandardChainWorkspace } from './pages/StandardChainWorkspace';
import { ArticleWorkflowPage } from './pages/ArticleWorkflowPage';
import { TaskDetailPage } from './pages/TaskDetailPage';
import { EvidenceDetailPage } from './pages/EvidenceDetailPage';
import { DeliveryCenterPage } from './pages/DeliveryCenterPage';
import { KnowledgeAssetsPage } from './pages/KnowledgeAssetsPage';
import { RewriteWorkspacePage } from './pages/RewriteWorkspacePage';
import { EditorialReviewPage } from './pages/EditorialReviewPage';
import { VersionComparePage } from './pages/VersionComparePage';
import { IndependentReviewPage } from './pages/IndependentReviewPage';
import { TriggerPage } from './pages';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="/tasks/new" element={<NewTaskPage />} />
          <Route path="/tasks/:taskId/chain" element={<StandardChainWorkspace />} />
          <Route path="/tasks/:taskId/rewrite" element={<RewriteWorkspacePage />} />
          <Route path="/tasks/:taskId/review" element={<EditorialReviewPage />} />
          <Route path="/tasks/:taskId/compare" element={<VersionComparePage />} />
          <Route path="/tasks/:taskId" element={<TaskDetailPage />} />
          <Route path="/workflow/article" element={<ArticleWorkflowPage />} />
          <Route path="/evidence/:factId" element={<EvidenceDetailPage />} />
          <Route path="/delivery" element={<DeliveryCenterPage />} />
          <Route path="/knowledge-assets" element={<KnowledgeAssetsPage />} />
          <Route path="/review/independent" element={<IndependentReviewPage />} />
          <Route path="/legacy" element={<TriggerPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;