%  Mutualist model modified with r-b verhulst formulation

b12 = 0.000041850;
c1 = 0.00004;
alpha1 = 0.000035/365;
r1 = 0.02-0.036;

r1day= r1/365;
N1_0=420;
N1log_ant=N1_0;
N1log=N1_0;
b12day=b12/365;

b21=0.00008750;
%b21= 0.000063185
c2 = 0.0001;
alpha2 = 0.000035/365;
r2 =0.05-0.07;

r2day=r2/365;
N2_0=1640;
N2log_ant=N2_0;
N2log = N2_0;
b21day=b21/365;

alpha2 =alpha2/365;


dias=35000;
for k=1:dias
    %r1eq = r1day+r1day*b12day*N2log/K1-r1day*N1log/K1;
    termeq1 = b12day*N2log_ant;
    r1eq = r1day+termeq1;
    
    %r1eq =r1day;
    
    %roz1 = (c1+incroz12*N2log)*N1log_ant;
    roz1 = (alpha1+termeq1*c1)*N1log_ant;
    rspneq1 = r1eq - roz1;
    incN1=binornd(N1log_ant,1-exp(-1*abs(rspneq1)));
    %decN1 = binornd(N1log,1-exp(-1*abs(roz1)));
    N1log = N1log_ant +sign(rspneq1)*incN1;
    K1cal = r1eq/(alpha1+termeq1*c1);
   
    %r2eq = r2day+r2day*b21day*N1log/K2-r2day*N2log/K2;
    %r2eq = r2day+b21day*N1log_ant;
    termeq2 = b21day*N1log_ant;
    r2eq = r2day+termeq2;
    
    %r2eq = r2day;
    
    %roz2 = (alpha2+incroz21*N1log_ant)*N2log;
    roz2 = (alpha2+termeq2*c2)*N2log_ant;
    rspneq2 = r2eq - roz2;
    incN2=binornd(N2log_ant,1-exp(-1*abs(rspneq2)));
    %decN2=binornd(N2log,1-exp(-1*abs(roz2)));
    N2log = N2log_ant +sign(rspneq2)*incN2;
    K2cal = r2eq/(alpha2+termeq2*c2);
    
    N1log_ant = N1log;
    N2log_ant =N2log;
    hold on;
    plot(k,N1log,'-r','LineWidth',4);
    plot(k,N2log,'-r','LineWidth',4);
   
    %plot(k,rspneq1,'-.r','LineWidth',4);
    %plot(k,roz1,'-.k','LineWidth',4);
    %plot(k,K1cal,'-k','LineWidth',1);
    %scatter(N1log,N2log,'.');
    
    
    hold on;
    %plot(k,roz2,'-b','LineWidth',4);
    %plot(k,rspneq2,'-b','LineWidth',4);
    %plot(k,N2log,'-b','LineWidth',4);
   % plot(k,K2cal,'-g','LineWidth',4);
   % plot(k,incN2,'-g','LineWidth',4);


end
    
%title(sprintf('N1inic=%d K1=%d r1=%0.2f b12=%0.2f (red); N2inic=%d K2=%d r2=%0.2f b21=%0.2f (blue)',N1_0,K1,r1,b12,N2_0,K2,r2,b21));

