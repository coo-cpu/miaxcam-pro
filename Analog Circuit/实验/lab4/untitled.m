clear; clf; 

% =======================================================
% 第一部分：计算串联电阻 Rs (读取 CSV 数据)
% =======================================================
filename = "PN数据.csv"; 

if isfile(filename)
    data_table = readtable(filename); 
    V_iv = table2array(data_table(:,1))'; 
    I_iv = table2array(data_table(:,2))';

    % 选取线性区域
    start_row = 55;  
    end_row = 59;    

    V_part = V_iv(start_row:end_row);
    I_part = I_iv(start_row:end_row);
    p = polyfit(V_part, I_part, 1); 
    Rs = 1 / p(1); 

    fprintf('--------------------------\n');
    fprintf('电阻 Rs = %.4f 欧姆\n', Rs);
    fprintf('--------------------------\n');

    figure(1);
    plot(V_iv(start_row:end_row), I_iv(start_row:end_row), 'bo', 'LineWidth', 2); hold on;
    y_fit = polyval(p, V_iv(start_row:end_row));
    plot(V_iv(start_row:end_row), y_fit, 'g-', 'LineWidth', 2);
    title(['Rs 计算: ' num2str(Rs) ' Ohms']);
    grid on;
else
    fprintf('⚠️ 未找到 "PN数据.csv"，跳过 Rs 计算部分...\n');
end

% =======================================================
% 第二部分：计算结电容 Cj
% =======================================================

% 1. 输入数据
V_dc = [20, 15, 10, 5, 4 , 2, 1,  0.3]; 
f_res = [ 527229.9, 493173.8, 449779.9 ,384591.8,366437.6, 316956.7, 278612.1, 100860.0]; 

% 自动对齐长度
min_len = min(length(V_dc), length(f_res));
V_dc = V_dc(1:min_len);
f_res = f_res(1:min_len);

% 2. 计算 Cj (L=0.01H)
L = 0.01; 
Cj = 1 ./ ((2 * pi * f_res).^2 * L);
Cj_inv_sq = 1 ./ (Cj.^2);

% 显示结果
fprintf('--------------------------------------\n');
fprintf('电压(V)\t\t频率(Hz)\t\t电容(pF)\n');
for i = 1:length(V_dc)
    fprintf('%.1f V\t\t%.0f\t\t%.2f pF\n', V_dc(i), f_res(i), Cj(i)*1e12);
end
fprintf('--------------------------------------\n');

% =======================================================
% 第三部分：画图 Cj - Vd (纯连线版，无拟合)
% =======================================================
figure(2); 

% 逻辑：舍去最后一个点 (0.3V)
if length(V_dc) > 1
    valid_idx = 1:length(V_dc)-1; 
else
    valid_idx = 1:length(V_dc);
end

% 排序：必须从小到大排，不然连线会乱
[V_plot, sort_idx] = sort(V_dc(valid_idx)); 
Cj_plot = Cj(valid_idx(sort_idx));          

% 1. 画散点 (蓝圈)
scatter(V_plot, Cj_plot, 'bo', 'LineWidth', 1.5); 
hold on; 

% 2. 直接连线 (绿线)
% 🌟 修改：直接连接原始数据点，不做任何拟合计算 🌟
plot(V_plot, Cj_plot, 'g-', 'LineWidth', 1.5);

xlabel("反向偏压 Vd (V)");
ylabel("结电容 Cj (F)");
title('Cj - Vd 关系图 (原始数据连线)');
grid on;

% =======================================================
% 第四部分：画图 1/Cj^2 - Vd (线性拟合求 Cj0)
% =======================================================
figure(3); 

% 同样获取排序后的 y轴数据
Cj_inv_sq_plot = Cj_inv_sq(valid_idx(sort_idx)); 

scatter(V_plot, Cj_inv_sq_plot, 'ro', 'LineWidth', 2); hold on;

% 线性拟合 (这一步必须保留拟合，否则算不出 Cj0)
if length(V_plot) >= 2
    p2 = polyfit(V_plot, Cj_inv_sq_plot, 1);
    
    % 这里还是用拟合直线，因为求 Cj0 需要直线的截距
    y_linear_line = polyval(p2, V_plot);
    plot(V_plot, y_linear_line, 'b-', 'LineWidth', 1.5);
    
    % 计算最终结果
    intercept = p2(2); 
    Cj0 = sqrt(1 / intercept);

    fprintf('\n🎉 最终计算结果 🎉\n');
    fprintf('线性拟合截距 b = %.4e\n', intercept);
    fprintf('零偏压结电容 Cj0 = %.2f pF\n', Cj0 * 1e12);
    fprintf('--------------------------------------\n');
else
    fprintf('⚠️ 有效数据点不足，无法拟合 Cj0\n');
end

xlabel("反向偏压 Vd (V)");
ylabel("1 / Cj^2");
title('线性拟合求 Cj0');
grid on;