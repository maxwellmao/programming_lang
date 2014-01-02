function data_fitting_ccdf(repos)
    data=sort(load(strcat('~/wxmao/umass/research/software/repository/diff_version/', repos, '/ModifiedTimes_data')));
    n=size(data, 1)
    fit_data=data(1:size(data, 1));
    
    figure(1);
    p = ((1:n)-0.5)' ./ n;
    [F,yi] = ecdf(data);
    [slope, intercept] = logfit(yi, 1-F, 'loglog');

    muMLE = expfit(fit_data)
    [parmhat,parmci] = lognfit(fit_data)
    mu=parmhat(1)
    sigma=parmhat(2)
    xgrid = linspace(0,1.1*max(data),10000)';
    [lambdahat,lambdaci] = poissfit(fit_data)
    h=figure;
%    stairs(data,p,'k-');
%    stairs(yi, 1-F, 'k-')
    loglog(yi, 1-F, 'k-')
    hold on
    y = -log(1 - p);
    muHat = y \ data;
    loglog(xgrid, 1-expcdf(xgrid,muHat),'r--', xgrid, 1- expcdf(xgrid, muMLE),'b--');
    hold on
     yApprox = (10^intercept)*xgrid.^(slope);
    loglog(xgrid, yApprox, 'g--')
%    loglog(xgrid, 1-poisscdf(xgrid, lambdahat), 'g--')
    hold on
    loglog(xgrid, 1-logncdf(xgrid,mu,sigma), 'c--')
    hold on

    paramEsts = gpfit(fit_data);
    kHat = paramEsts(1)   % Tail index parameter
    sigmaHat = paramEsts(2)   % Scale parameter
    loglog(xgrid, 1-gpcdf(xgrid, kHat, sigmaHat),'m--');
    hold on

    P=0.0005
%    plot(xgrid, geocdf(xgrid, P), 'm--')%
    xlabel('x');
    ylim([10e-5, 1])
    ylabel('Cumulative probability (p)');
    legend({'Data','Exp LS Fit','Exp ML Fit', 'Power Law Fit', 'Lognormal Fit', 'Generalized Pareto'}, 'location', 'southwest');
    saveas(h, strcat('~/wxmao/umass/research/software/repository/diff_version/', repos, '/fit.png'),'png');
end

%function turn_cdf_to_ccdf(cdf)
%    pdf=cdf
%    for i=2:length(ccdf)
%        pdf(i)=pdf(i)-pdf(i-1)
%    end
%    ccdf=pdf
%    for i=length(ccdf)-1:-1:1
%        ccdf(i)=ccdf(i+1)+ccdf(i)
%    end
%    return ccdf
%end
