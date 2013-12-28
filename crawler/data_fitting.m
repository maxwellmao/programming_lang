function data_fitting()
    data=sort(load('~/wxmao/umass/research/software/repository/diff_version/presto/ModifiedTimes_data'));
    n=size(data, 1)
    fit_data=data(1:size(data, 1));
    
    p = ((1:n)-0.5)' ./ n;
    [F,yi] = ecdf(data);
    muMLE = expfit(fit_data)
    [parmhat,parmci] = lognfit(fit_data)
    mu=parmhat(1)
    sigma=parmhat(2)
    xgrid = linspace(0,1.1*max(data),10000)';
    [lambdahat,lambdaci] = poissfit(fit_data)
    h=figure;
%    stairs(data,p,'k-');
    stairs(yi, F, 'k-')
    hold on
    y = -log(1 - p);
    muHat = y \ data;
    plot(xgrid, expcdf(xgrid,muHat),'r--', xgrid,expcdf(xgrid,muMLE),'b--');
    hold on
    plot(xgrid, poisscdf(xgrid, lambdahat), 'g--')
    hold on
    plot(xgrid, logncdf(xgrid,mu,sigma), 'y--')
    hold on

    paramEsts = gpfit(fit_data);
    kHat = paramEsts(1)   % Tail index parameter
    sigmaHat = paramEsts(2)   % Scale parameter
    plot(xgrid,gpcdf(xgrid, kHat, sigmaHat),'c-');
    hold on
    P=0.0005
%    plot(xgrid, geocdf(xgrid, P), 'm--')%
    xlabel('x');
    ylabel('Cumulative probability (p)');
    legend({'Data','Exp LS Fit','Exp ML Fit', 'Poisson Fit', 'Lognormal Fit', 'Pareto'}, 'location', 'southeast');
    saveas(h, '~/wxmao/umass/research/software/repository/diff_version/presto/fit.png','png');
end
