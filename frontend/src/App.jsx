import React, { useState } from 'react';
import Header from './components/Header';
import InterpolatePage from './pages/InterpolatePage';
import EvaluatePage from './pages/EvaluatePage';

function App() {
    const [activeTab, setActiveTab] = useState('interpolate'); // 'interpolate' or 'evaluate'

    return (
        <>
            <Header
                activeTab={activeTab}
                onTabChange={setActiveTab}
            />
            {activeTab === 'interpolate' ? <InterpolatePage /> : <EvaluatePage />}
        </>
    );
}

export default App;
