document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const submitBtn = document.getElementById('submit-btn');
    const resultSection = document.querySelector('.result-section');
    const uploadedImage = document.getElementById('uploaded-image');
    const resultCanvas = document.getElementById('result-canvas');
    const detectionResults = document.getElementById('detection-results');
    const loading = document.querySelector('.loading');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = imageUpload.files[0];
        if (!file) {
            alert('请选择一个图片文件');
            return;
        }
        
        // 显示加载状态
        loading.style.display = 'block';
        resultSection.style.display = 'none';
        
        const formData = new FormData();
        formData.append('file', file);
        
        // 发送请求到后端
        fetch('/api/detect', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            
            if (data.status === 'success') {
                // 显示结果区域
                resultSection.style.display = 'block';
                
                // 显示上传的图片
                const fileReader = new FileReader();
                fileReader.onload = function(event) {
                    uploadedImage.src = event.target.result;
                    
                    // 图片加载完成后绘制边界框
                    uploadedImage.onload = function() {
                        drawDetections(data.results);
                    };
                };
                fileReader.readAsDataURL(file);
                
                // 显示检测结果详情
                displayResultDetails(data.results);
            } else {
                alert('处理失败: ' + data.message);
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            alert('请求发生错误: ' + error);
        });
    });
    
    function drawDetections(results) {
        const ctx = resultCanvas.getContext('2d');
        ctx.clearRect(0, 0, resultCanvas.width, resultCanvas.height);
        
        // 调整canvas大小匹配图片
        resultCanvas.width = uploadedImage.width;
        resultCanvas.height = uploadedImage.height;
        
        // 设置绘制样式
        ctx.lineWidth = 3;
        ctx.font = '16px Arial';
        
        results.forEach(result => {
            // 随机颜色
            const color = `rgb(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)})`;
            ctx.strokeStyle = color;
            ctx.fillStyle = color;
            
            // 绘制边界框
            const [x1, y1, x2, y2] = result.bbox;
            ctx.beginPath();
            ctx.rect(x1, y1, x2 - x1, y2 - y1);
            ctx.stroke();
            
            // 绘制标签和置信度
            const label = `类别 ${result.label}: ${(result.score * 100).toFixed(1)}%`;
            ctx.fillText(label, x1, y1 > 20 ? y1 - 5 : y1 + 20);
        });
    }
    
    function displayResultDetails(results) {
        detectionResults.innerHTML = '';
        
        if (results.length === 0) {
            detectionResults.innerHTML = '<p>未检测到任何对象</p>';
            return;
        }
        
        const resultList = document.createElement('ul');
        results.forEach((result, index) => {
            const item = document.createElement('li');
            item.textContent = `对象 ${index + 1}: 类别 ${result.label}, 置信度 ${(result.score * 100).toFixed(1)}%`;
            resultList.appendChild(item);
        });
        
        detectionResults.appendChild(resultList);
    }
}); 